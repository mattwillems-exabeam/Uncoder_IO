# Uncoder.io LogRhythm AIE Testing Checklist

## Pre-Test Setup

After Docker Desktop reboot completes:

```bash
cd C:\Users\Administrator\Downloads\Uncoder_IO
docker-compose up -d
```

Wait for containers to start, then open: http://localhost:4010/

## Quick Test Procedure

### 1. Verify Platform Available
- [ ] Open http://localhost:4010/
- [ ] Select "Sigma rule" as input type
- [ ] Check output format dropdown for "LogRhythm AI Engine Rule" or "LogRhythm AIE Rule"
- [ ] If not found, check Docker logs: `docker-compose logs translator`

### 2. Test Basic RDP Rule
- [ ] Paste contents of `test_sigma_rdp.yml` into input panel
- [ ] Select "LogRhythm AI Engine Rule" as output format
- [ ] Click "Translate"
- [ ] Verify JSON output appears (not error message)
- [ ] Check key fields:
  - [ ] `"name": "Suspicious RDP Login"`
  - [ ] `"risk_rating": 7` (high severity)
  - [ ] `"block_type": "LogObservedRuleBlock"`
  - [ ] Filter with `filter_type: 37` (EventID → VendorMsgID)
  - [ ] Filter with `filter_type: 110` (LogonType → Severity)
  - [ ] `"group_by_fields": [16]` or `[17]` (authentication context)

### 3. Test Process Detection Rule
- [ ] Load `test_sigma_process.yml`
- [ ] Translate to LogRhythm AIE
- [ ] Verify:
  - [ ] `"risk_rating": 9` (critical)
  - [ ] `filter_type: 41` (Image → Process)
  - [ ] `filter_type: 112` (CommandLine → Command)
  - [ ] `match_type: 2` (Regex for contains)
  - [ ] Multiple CommandLine values handled correctly
  - [ ] `"group_by_fields": [17]` (system activity)

### 4. Test Network Rule
- [ ] Load `test_sigma_network.yml`
- [ ] Translate to LogRhythm AIE
- [ ] Verify:
  - [ ] `"risk_rating": 5` (medium)
  - [ ] `filter_type: 19` (DestinationIp → DIP)
  - [ ] `filter_type: 27` (DestinationPort → DPort)
  - [ ] Multiple IPs handled with OR logic
  - [ ] `"group_by_fields": [16]` (network traffic)

### 5. Test NOT Condition
- [ ] Load `test_sigma_not.yml`
- [ ] Translate to LogRhythm AIE
- [ ] Verify:
  - [ ] EventID filter with `filter_mode: 0` (normal)
  - [ ] WorkstationName filter with `filter_mode: 1` (negated)
  - [ ] Both use `field_operator: "And"`

## Cross-Validation with Python Converter

For each test, compare with our Python converter:

```bash
cd C:\Users\Administrator\Downloads\windows-test-package\windows-test-package

# Test 1
python sigma_to_json_pysigma.py C:\Users\Administrator\Downloads\Uncoder_IO\test_sigma_rdp.yml test_outputs\uncoder_comparison_rdp.json

# Test 2
python sigma_to_json_pysigma.py C:\Users\Administrator\Downloads\Uncoder_IO\test_sigma_process.yml test_outputs\uncoder_comparison_process.json

# Compare JSON structures (not byte-for-byte, but logical equivalence)
```

## End-to-End AIRX Test

Save Uncoder output and test with C# converter:

```bash
cd C:\Users\Administrator\Downloads\windows-test-package\windows-test-package

# Create AIRX from Uncoder JSON
dotnet_interop\bin\Release\net472\AirxInterop.exe create <uncoder_output.json> test_outputs\uncoder_test.airx

# Parse to verify
dotnet_interop\bin\Release\net472\AirxInterop.exe parse test_outputs\uncoder_test.airx
```

## Success Criteria

✅ **Must Have**:
1. Platform appears in Uncoder.io UI
2. SIGMA rules convert to valid JSON (no errors)
3. Field mappings are correct (filter_type values match documentation)
4. JSON structure matches what C# converter expects
5. Generated AIRX parses successfully

✅ **Nice to Have**:
1. Output closely matches Python converter output
2. Field operator logic is correct
3. Group by field selection is context-aware
4. MITRE ATT&CK metadata preserved

## Known Issues to Accept (if any)

Document any differences between Uncoder and Python converter:
- Different group_by_fields selection strategy (both valid)
- Different field_operator patterns (both valid if logical equivalent)
- Metadata formatting differences

## Troubleshooting

### Platform Not Showing
```bash
# Check translator logs
docker-compose logs translator | grep -i error
docker-compose logs translator | grep -i logrhythm

# Rebuild if needed
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Import Errors
```bash
# Check Python import errors
docker exec -it uncoder-core python -c "from app.translator.platforms.logrhythm_aie import LogRhythmAIERuleRender"
```

### Validation Errors
- Compare JSON against our test files
- Check field IDs in FIELD_REFERENCE.md
- Verify field_operator values match patterns in documentation
