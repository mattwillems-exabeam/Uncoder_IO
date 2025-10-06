"""
Uncoder IO Community Edition License
-----------------------------------------------------------------
Copyright (c) 2024 SOC Prime, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------
"""

from app.translator.core.mapping import BasePlatformMappings, LogSourceSignature
from app.translator.platforms.logrhythm_aie.const import UNMAPPED_FIELD_DEFAULT, logrhythm_aie_rule_details


class LogRhythmAIELogSourceSignature(LogSourceSignature):
    """Log source signature for LogRhythm AIE (placeholder - not actively used)"""

    def __init__(self):
        pass

    def is_suitable(self, log_source_signature: dict) -> bool:
        """All log sources are suitable for AIE rules"""
        return True

    def __str__(self) -> str:
        return ""


class LogRhythmAIEMappings(BasePlatformMappings):
    """
    LogRhythm AIE field mappings - SIGMA fields to FieldFilterTypeEnum.

    Note: FieldFilterTypeEnum (used in filter_type) is DIFFERENT from
    FieldEnum (used in group_by_fields)!
    """

    def __init__(self, platform_dir: str = None, platform_details=None):
        if platform_details is None:
            platform_details = logrhythm_aie_rule_details
        super().__init__(platform_dir, platform_details)

    # FieldFilterTypeEnum mappings (for msg_filters → field_filters)
    # These are the filter_type values used when building field_filters
    skip_load_default_mappings = True

    def prepare_log_source_signature(self, mapping: dict) -> LogSourceSignature:
        """Prepare log source signature from mapping"""
        return LogRhythmAIELogSourceSignature()

    def check_fields_mapping_existence(self, query_fields, function_fields_map, supported_functions, source_mapping):
        """
        Override field mapping check - all fields are handled programmatically via get_field_id().
        Return empty list to suppress 'unmapped fields' comment.
        """
        return []

    def get_field_id(self, sigma_field: str) -> int:
        """Get LogRhythm FieldFilterTypeEnum ID for SIGMA field"""

        # Process fields
        if sigma_field in ["Image", "ProcessName"]:
            return 41  # Process
        if sigma_field == "ProcessId":
            return 109  # PID
        if sigma_field == "CommandLine":
            return 112  # Command
        if sigma_field == "ParentImage":
            return 146  # ParentProcessName
        if sigma_field == "ParentCommandLine":
            return 147  # ParentProcessPath
        if sigma_field == "ParentProcessId":
            return 145  # ParentProcessId

        # Network fields
        if sigma_field in ["SourceIp", "SourceAddress", "src_ip"]:
            return 18  # SIP
        if sigma_field in ["DestinationIp", "DestinationAddress", "DestAddress", "dst_ip"]:
            return 19  # DIP
        if sigma_field in ["SourcePort", "src_port"]:
            return 26  # SPort
        if sigma_field in ["DestinationPort", "DestPort", "dst_port"]:
            return 27  # DPort
        if sigma_field == "Protocol":
            return 28  # Protocol

        # Authentication fields - CRITICAL DISTINCTION
        # Login (29) = User performing action (actor/origin)
        # Account (30) = User being acted upon (target/impacted)
        if sigma_field in ["User", "UserName", "SourceUser", "SubjectUserName"]:
            return 29  # Login (actor - DEFAULT for generic User)
        if sigma_field in ["TargetUserName", "TargetUser", "AccountName"]:
            return 30  # Account (target/impacted)
        if sigma_field == "LogonType":
            return 110  # Severity (dual purpose field)
        if sigma_field == "WorkstationName":
            return 25  # DHostName
        if sigma_field == "IpAddress":
            return 18  # SIP

        # Host/System fields
        if sigma_field == "Host":
            return 98  # Host
        if sigma_field == "HostName":
            return 23  # HostName
        if sigma_field in ["Computer", "ComputerName"]:
            return 98  # Host
        if sigma_field == "SHost":
            return 99  # SHost
        if sigma_field == "DHost":
            return 100  # DHost
        if sigma_field == "SHostName":
            return 24  # SHostName
        if sigma_field == "DHostName":
            return 25  # DHostName

        # Event fields
        if sigma_field in ["EventID", "VendorMessageID", "VendorMsgID"]:
            return 37  # VendorMsgID

        # File/Object/Registry fields
        if sigma_field in ["TargetFilename", "FileName", "TargetObject", "ImageLoaded",
                          "DestinationFilename", "Details", "NewValue"]:
            return 113  # ObjectName
        if sigma_field == "ObjectType":
            return 142  # ObjectType

        # Hash fields
        if sigma_field in ["Hashes", "md5", "MD5", "sha1", "SHA1", "sha256", "SHA256", "Imphash"]:
            return 138  # Hash

        # Web/HTTP fields
        if sigma_field in ["URL", "url"]:
            return 42  # URL
        if sigma_field in ["UserAgent", "User-Agent"]:
            return 144  # UserAgent

        # Domain fields
        if sigma_field == "Domain":
            return 39  # Domain
        if sigma_field == "SourceHostname":
            return 24  # SHostName
        if sigma_field == "DestinationHostname":
            return 25  # DHostName

        # Windows service fields
        if sigma_field == "ServiceName":
            return 113  # ObjectName
        if sigma_field == "ServiceFileName":
            return 41  # Process

        # DNS fields
        if sigma_field == "QueryName":
            return 113  # ObjectName
        if sigma_field == "QueryResults":
            return 112  # Command (fallback)
        if sigma_field == "QueryStatus":
            return 150  # Status

        # Windows Security Event fields
        if sigma_field == "Application":
            return 41  # Process
        if sigma_field in ["FilterOrigin", "Initiated", "Channel"]:
            return 112  # Command (fallback)
        if sigma_field == "Level":
            return 110  # Severity

        # Sysmon/Advanced fields (fallback to Command)
        if sigma_field in ["IntegrityLevel", "GrantedAccess", "CallTrace"]:
            return 112  # Command (needs research)

        # Code signing fields (fallback to Command)
        if sigma_field in ["Signed", "Signature", "SignatureStatus"]:
            return 112  # Command (needs research)

        # Fallback: Command (112) for unknown fields
        # Command is moderately expensive but often matches process/command-related fields
        # Alternative: Message (35) searches entire raw log (very expensive, last resort only)
        return UNMAPPED_FIELD_DEFAULT


# Create singleton instance
logrhythm_aie_mappings = LogRhythmAIEMappings(
    platform_dir="logrhythm_aie", platform_details=logrhythm_aie_rule_details
)
