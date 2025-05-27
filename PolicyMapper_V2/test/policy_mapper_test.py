import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_evaluate_claim_approved():
    damage = {
        "_id": "123",
        "part": "door",
        "damageType": ["scratch"],
        "severity": "minor",
        "decision": "Repair",
        "reason": "cosmetic",
        "cost": 100.0,
        "obd_code": False,
        "internal": "None",
        "flag": "None"
    }
    claim_data = {
        "insuranceId": "ins123",
        "damagedAreas": ["door"],
        "location": {"latitude": "0", "longitude": "0"},
        "weather": "clear",
        "fraud_verification": {"check1": True, "check2": True}
    }
    vehicle_data = {
        "vehicleModel": "Model X",
        "vehicleColor": "Red",
        "insurancePolicy": "Full Coverage",
        "vinNumber": "VIN123",
        "vehicleNumberPlate": "ABC123"
    }

    # Mock LLM streaming response yielding valid JSON content
    async def mock_stream():
        yield type('obj', (object,), {'choices': [{'delta': {'content': '```json\n{"status": "approved", "decision": "Repair", "reason": "Valid claim", "cost": 100, "approved": true}\n```'}}]})()

    with patch('module_path.client.chat.completions.create', return_value=mock_stream()):
        result = await evaluate_claim_using_llma(claim_data, [damage], vehicle_data)
        assert result['overall_status'] == "Approved"
        assert result['approved_costs'] == 100
        assert result['damage_evaluations'][0]['evaluation']['status'] == "approved"

@pytest.mark.asyncio
async def test_missing_damage_fields_defaults():
    damage = {
        # Missing 'part', 'damageType', 'severity', 'decision', 'reason', 'cost'
        "_id": "123",
        "obd_code": False,
        "internal": "None",
        "flag": "None"
    }
    claim_data = {
        "insuranceId": "ins123",
        "damagedAreas": [],
        "location": {},
        "fraud_verification": {"check1": True}
    }
    vehicle_data = {}

    async def mock_stream():
        yield type('obj', (object,), {'choices': [{'delta': {'content': '```json\n{"status": "approved", "decision": "Repair", "reason": "All good", "cost": 0, "approved": true}\n```'}}]})()

    with patch('module_path.client.chat.completions.create', return_value=mock_stream()):
        result = await evaluate_claim_using_llma(claim_data, [damage], vehicle_data)

        evaluation = result['damage_evaluations'][0]['evaluation']
        assert evaluation['status'] == "approved"
        assert result['damage_evaluations'][0]['part_damaged'] == "Unknown Part"
        assert result['damage_evaluations'][0]['cost'] == 0.0



@pytest.mark.asyncio
async def test_fraud_flags_false_rejection():
    damage = {
        "_id": "456",
        "part": "bumper",
        "damageType": ["dent"],
        "severity": "major",
        "decision": "Replace",
        "reason": "Severe damage",
        "cost": 5000,
        "obd_code": True,
        "internal": "None",
        "flag": "None"
    }
    claim_data = {
        "insuranceId": "ins456",
        "damagedAreas": ["bumper"],
        "location": {},
        "fraud_verification": {"check1": False, "check2": False}
    }
    vehicle_data = {}

    async def mock_stream():
        yield type('obj', (object,), {'choices': [{'delta': {'content': '```json\n{"status": "approved", "decision": "Repair", "reason": "Valid claim", "cost": 5000, "approved": true}\n```'}}]})()

    with patch('module_path.client.chat.completions.create', return_value=mock_stream()):
        result = await evaluate_claim_using_llma(claim_data, [damage], vehicle_data)
        evaluation = result['damage_evaluations'][0]['evaluation']

        assert evaluation['status'] == "rejected"
        assert evaluation['decision'] == "rejected"
        assert evaluation['reason'] == "Fraud detected. One or more verifications failed."
        assert evaluation['approved'] is False
        assert result['overall_status'] == "Rejected"



@pytest.mark.asyncio
async def test_multiple_damages_mixed_approval():
    damages = [
        {
            "_id": "1",
            "part": "door",
            "damageType": ["scratch"],
            "severity": "minor",
            "decision": "Repair",
            "reason": "cosmetic",
            "cost": 150,
            "obd_code": False,
            "internal": "None",
            "flag": "None"
        },
        {
            "_id": "2",
            "part": "engine",
            "damageType": ["crack"],
            "severity": "severe",
            "decision": "Replace",
            "reason": "critical",
            "cost": 5000,
            "obd_code": True,
            "internal": "Internal damage",
            "flag": "None"
        }
    ]

    claim_data = {
        "insuranceId": "ins789",
        "damagedAreas": ["door", "engine"],
        "location": {},
        "fraud_verification": {"check1": True, "check2": True}
    }
    vehicle_data = {}

    # Mock the streaming LLM to respond differently per call
    async def mock_stream_approved():
        yield type('obj', (object,), {'choices': [{'delta': {'content': '```json\n{"status": "approved", "decision": "Repair", "reason": "Valid claim", "cost": 150, "approved": true}\n```'}}]})()
    async def mock_stream_rejected():
        yield type('obj', (object,), {'choices': [{'delta': {'content': '```json\n{"status": "rejected", "decision": "Replace", "reason": "Not covered", "cost": 5000, "approved": false}\n```'}}]})()

    with patch('module_path.client.chat.completions.create', side_effect=[mock_stream_approved(), mock_stream_rejected()]):
        result = await evaluate_claim_using_llma(claim_data, damages, vehicle_data)

        assert result['overall_status'] == "Approved"  # since one approved
        assert result['approved_costs'] == 150
        assert len(result['damage_evaluations']) == 2
        assert result['damage_evaluations'][0]['evaluation']['approved'] is True
        assert result['damage_evaluations'][1]['evaluation']['approved'] is False



@pytest.mark.asyncio
async def test_invalid_json_fallback():
    damage = {
        "_id": "999",
        "part": "hood",
        "damageType": ["dent"],
        "severity": "minor",
        "decision": "Repair",
        "reason": "cosmetic",
        "cost": 200,
        "obd_code": False,
        "internal": "None",
        "flag": "None"
    }
    claim_data = {
        "insuranceId": "ins999",
        "damagedAreas": ["hood"],
        "location": {},
        "fraud_verification": {"check1": True}
    }
    vehicle_data = {}

    # LLM response is invalid JSON
    async def mock_stream_invalid_json():
        yield type('obj', (object,), {'choices': [{'delta': {'content': '```json\n{invalid json}\n```'}}]})()

    with patch('module_path.client.chat.completions.create', return_value=mock_stream_invalid_json()):
        result = await evaluate_claim_using_llma(claim_data, [damage], vehicle_data)

        evaluation = result['damage_evaluations'][0]['evaluation']
        assert evaluation['status'] == "rejected"
        assert evaluation['approved'] is False
        assert "coverage requirements" in evaluation['reason']



@pytest.mark.asyncio
async def test_empty_damage_detection_data():
    claim_data = {
        "insuranceId": "empty123",
        "damagedAreas": [],
        "location": {},
        "fraud_verification": {"check1": True}
    }
    vehicle_data = {}

    result = await evaluate_claim_using_llma(claim_data, [], vehicle_data)

    assert result['overall_status'] == "Rejected"  # no damages, so no approval
    assert result['total_cost'] == 0
    assert result['approved_costs'] == 0
    assert result['damage_evaluations'] == []
