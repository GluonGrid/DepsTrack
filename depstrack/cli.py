import subprocess

import requests
from colorama import Back, Fore, Style, init
from cvss import CVSS3, CVSS4
from packaging.version import parse as parse_version

init(autoreset=True)  # Initialize colorama

OSV_API_URL = "https://api.osv.dev/v1/querybatch"
OSV_VULN_URL = "https://api.osv.dev/v1/vulns/"

SEVERITY_COLORS = {
    "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
    "HIGH": Fore.RED,
    "MEDIUM": Fore.YELLOW,
    "LOW": Fore.CYAN,
    "UNKNOWN": Fore.WHITE,
}


def get_installed_packages():
    try:
        result = subprocess.run(
            ["pip", "freeze"], capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            print(
                Fore.YELLOW
                + "Warning: No output from 'uv pip freeze'. Is 'uv' installed?"
            )
            return {}

        dependencies = {}
        for line in result.stdout.splitlines():
            if "==" in line:
                package, version = line.split("==")
                dependencies[package] = version

        return dependencies
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error: Failed to run 'uv pip freeze'. {e}")
        return {}


def get_pypi_metadata(package, installed_version):
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        metadata = response.json()

        is_yanked = False
        if installed_version in metadata.get("releases", {}):
            release_data = metadata["releases"].get(installed_version, [])
            is_yanked = any(r.get("yanked", False) for r in release_data)

        return metadata, is_yanked
    except requests.RequestException:
        return None, False


def fetch_vulnerability_details(vuln_id):
    try:
        response = requests.get(f"{OSV_VULN_URL}{vuln_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def check_for_vulnerabilities(dependencies):
    payload = {
        "queries": [
            {"package": {"name": pkg, "ecosystem": "PyPI"}, "version": ver}
            for pkg, ver in dependencies.items()
        ]
    }
    try:
        response = requests.post(OSV_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])

        vulnerability_data = {}
        for i, dep in enumerate(results):
            package_name = list(dependencies.keys())[i]
            vulns = dep.get("vulns", [])
            detailed_vulnerabilities = []

            for v in vulns:
                vuln_details = fetch_vulnerability_details(v["id"])
                # Use summary; if missing, fallback to details
                summary = (
                    (
                        vuln_details.get("summary")
                        or vuln_details.get("details", "No summary available")
                    )
                    if vuln_details
                    else "No summary available"
                )
                references = (
                    [r["url"] for r in vuln_details.get("references", [])]
                    if vuln_details
                    else []
                )

                # Provided severity object fallback
                severity_obj = (
                    vuln_details.get(
                        "severity", [{"type": "UNKNOWN", "score": "N/A"}]
                    )[0]
                    if vuln_details
                    else {"type": "UNKNOWN", "score": "N/A"}
                )
                severity = severity_obj["type"].upper()

                # Convert CVSS vector into a numeric score and severity using local library
                cvss_score = "N/A"
                cvss_severity = "UNKNOWN"
                cvss_vector = severity_obj["score"]
                if severity == "CVSS_V3":
                    try:
                        cvss_instance = CVSS3(cvss_vector)
                        cvss_score = cvss_instance.scores()[0]
                        cvss_severity = cvss_instance.severities()[0]
                    except Exception:
                        pass
                elif severity == "CVSS_V4":
                    try:
                        cvss_instance = CVSS4(cvss_vector)
                        cvss_score = cvss_instance.base_score
                        cvss_severity = cvss_instance.severity
                    except Exception:
                        pass

                color = SEVERITY_COLORS.get(cvss_severity.upper(), Fore.WHITE)

                detailed_vulnerabilities.append(
                    {
                        "id": v["id"],
                        "summary": summary,
                        "references": references,
                        "severity": severity,
                        "cvss_score": cvss_score,
                        "cvss_severity": cvss_severity,
                        "color": color,
                    }
                )

            vulnerability_data[package_name] = detailed_vulnerabilities

        return vulnerability_data
    except requests.RequestException as e:
        print(Fore.RED + f"Error checking vulnerabilities: {e}")
        return {}


def check_for_updates():
    dependencies = get_installed_packages()
    vulnerabilities = check_for_vulnerabilities(dependencies)
    report = []

    for package, installed_version in dependencies.items():
        metadata, is_yanked = get_pypi_metadata(package, installed_version)
        if not metadata:
            continue

        latest_version = metadata["info"]["version"]
        changelog_url = metadata["info"].get(
            "release_url", f"https://pypi.org/project/{package}/#history"
        )
        release_date = (
            metadata["urls"][0]["upload_time"]
            if metadata.get("urls")
            else "Unknown"
        )
        has_vulnerabilities = bool(vulnerabilities.get(package, []))

        installed_v = parse_version(installed_version)
        latest_v = parse_version(latest_version)
        is_major_update = installed_v.major < latest_v.major
        is_latest_lower = installed_v > latest_v

        if (
            is_major_update
            or is_yanked
            or has_vulnerabilities
            or is_latest_lower
        ):
            report.append(
                {
                    "package": package,
                    "installed_version": installed_version,
                    "latest_version": latest_version,
                    "is_major_update": is_major_update,
                    "is_deprecated": is_yanked,
                    "release_date": release_date,
                    "changelog_url": changelog_url,
                    "has_vulnerabilities": has_vulnerabilities,
                    "vulnerabilities": vulnerabilities.get(package, []),
                    "is_latest_lower": is_latest_lower,
                }
            )

    return report


def print_report():
    report = check_for_updates()
    for item in report:
        deprecation_warning = (
            Fore.RED + Style.BRIGHT + "💥 Yanked version detected!"
            if item["is_deprecated"]
            else ""
        )
        latest_lower_warning = (
            Fore.MAGENTA + "❗ Latest version is lower than installed!"
            if item["is_latest_lower"]
            else ""
        )
        breaking_change_warning = (
            Fore.YELLOW + "⚠️ Major update may cause compatibility issues!"
            if item["is_major_update"]
            else ""
        )

        print(
            f"{Back.WHITE + Fore.BLACK + Style.BRIGHT}{item['package']}: {item['installed_version']} -> {item['latest_version']}{Back.RESET + Style.RESET_ALL} {deprecation_warning} {latest_lower_warning} {breaking_change_warning}"
        )
        print(f"{Fore.CYAN}Release Date: {item['release_date']}")
        print(f"{Fore.BLUE}Release notes: {item['changelog_url']}")

        if item["has_vulnerabilities"]:
            print(Fore.RED + Style.BRIGHT + "🚨 Vulnerabilities:")
            for vuln in item["vulnerabilities"]:
                print(
                    f"  {vuln['color']}- ({vuln['severity']}, Score: {vuln['cvss_score']}, Severity: {vuln['cvss_severity']}): {vuln['summary']}"
                )
                for ref in vuln["references"]:
                    print(f"    More info: {Fore.BLUE}{ref}")
        print()


def main():
    print_report()


if __name__ == "__main__":
    main()
