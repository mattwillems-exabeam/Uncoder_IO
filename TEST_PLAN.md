# Uncoder.io LogRhythm AIE Testing Plan

## Test Environment Setup

### 1. Start Uncoder.io with Docker
```bash
cd C:\Users\Administrator\Downloads\Uncoder_IO
docker-compose up -d
```

Access at: http://localhost:4010/

### 2. Verify Platform is Available
- Open Uncoder.io web interface
- Check if "LogRhythm AI Engine Rule" appears in output format dropdown
- Platform ID should be: `logrhythm-aie-rule`

## Test Cases

### Test 1: Basic RDP Detection Rule
**File**: `test_sigma_rdp.yml`

**SIGMA Input**:
```yaml
title: Suspicious RDP Login
id: 1234-5678-90ab-cdef
status: test
description: Detects suspicious RDP connections
author: Test Author
date: 2024/01/01
level: high
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4624
        LogonType: 10
    condition: selection
```

**Expected AIE JSON Output**:
```json
{
    "name": "Suspicious RDP Login",
    "short_desc": "Suspicious RDP Login",
    "long_desc": "Detects suspicious RDP connections\nAuthor: Test Author",
    "risk_rating": 7,
    "alarm_enabled": true,
    "rule_enabled": false,
    "blocks": [
        {
            "block_type": "LogObservedRuleBlock",
            "msg_filters": {
                "field_filters": [
                    {
                        "filter_type": 37,
                        "filter_mode": 0,
                        "filter_value": "4624",
                        "match_type": 0,
                        "field_operator": "And"
                    },
                    {
                        "filter_type": 110,
                        "filter_mode": 0,
                        "filter_value": "10",
                        "match_type": 0,
                        "field_operator": "And"
                    }
                ]
            },
            "group_by_fields": [16]
        }
    ]
}
```

**Validation Checks**:
- ✅ EventID (4624) maps to filter_type: 37 (VendorMsgID)
- ✅ LogonType (10) maps to filter_type: 110 (Severity)
- ✅ Both use field_operator: "And" (simple AND logic)
- ✅ Risk rating: 7 (high severity)
- ✅ Group by: 16 (Source - Host Origin for authentication)

### Test 2: Process Creation with Wildcards
**Create**: `test_sigma_process.yml`

```yaml
title: Mimikatz Process Detection
level: critical
logsource:
    product: windows
    service: sysmon
    definition: 'Sysmon EID 1'
detection:
    selection:
        EventID: 1
        Image|contains: 'mimikatz'
        CommandLine|contains:
            - 'sekurlsa'
            - 'lsadump'
    condition: selection
```

**Expected Output**:
- filter_type: 41 (Process) for Image
- filter_type: 112 (Command) for CommandLine
- match_type: 2 (Regex) for contains operations
- filter_value: "mimikatz" (wildcard converted to .* in regex)
- Multiple CommandLine values as separate filters with "Or" operator
- group_by_fields: [17] (Destination - Host Impacted for system activity)
- risk_rating: 9 (critical)

### Test 3: Network Traffic Rule
**Create**: `test_sigma_network.yml`

```yaml
title: Suspicious Outbound Connection
level: medium
logsource:
    category: firewall
detection:
    selection:
        DestinationIp:
            - '192.168.1.100'
            - '10.0.0.50'
        DestinationPort: 4444
    condition: selection
```

**Expected Output**:
- filter_type: 19 (DIP) for DestinationIp
- filter_type: 27 (DPort) for DestinationPort
- Multiple DIP values with "Or" logic
- group_by_fields: [16] (Source - Host Origin for network traffic)
- risk_rating: 5 (medium)

### Test 4: NOT Condition
**Create**: `test_sigma_not.yml`

```yaml
title: Logon Not from Expected Host
level: high
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4624
    filter:
        WorkstationName: 'ADMIN-PC'
    condition: selection and not filter
```

**Expected Output**:
- EventID filter with filter_mode: 0 (normal)
- WorkstationName filter with filter_mode: 1 (negated - IS NOT)
- Both use field_operator: "And"

## Comparison Testing

After each test:
1. Save Uncoder.io JSON output to `test_outputs/uncoder_*.json`
2. Run our Python converter on same SIGMA file: `python sigma_to_json_pysigma.py <file>.yml test_outputs/pysigma_*.json`
3. Compare outputs - structure should match
4. Test with C# converter: `dotnet_interop/bin/Release/net472/AirxInterop.exe create <json_file> <output.airx>`
5. Parse AIRX to verify: `dotnet_interop/bin/Release/net472/AirxInterop.exe parse <output.airx>`

## Known Differences to Document

- Uncoder may handle nested boolean logic differently than our Python converter
- Group by field selection might differ (both valid, different strategies)
- Field mappings should be identical (both use same FieldFilterTypeEnum)

## Success Criteria

✅ LogRhythm AIE appears in Uncoder.io output formats
✅ Basic SIGMA rule converts to valid AIE JSON
✅ Field mappings match our documented values
✅ Generated JSON serializes to AIRX successfully
✅ AIRX imports into LogRhythm without errors
✅ Rule logic matches SIGMA intent

## Debugging Steps if Issues Found

1. Check browser console for JavaScript errors
2. Check Docker logs: `docker-compose logs`
3. Verify platform files loaded: Check for import errors in logs
4. Test field mapping: Compare filter_type values with FIELD_REFERENCE.md
5. Validate JSON structure against our C# converter requirements
