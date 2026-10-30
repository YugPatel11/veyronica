import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_exam_workflow_api_process_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "run_id": "run_api_exam_001",
            "filename": "exam_sheet.pdf",
            "raw_ocr_text": "Roll: CS2026-999\nName: Riya\nQ1. Hash table uses hashing.\nQ2. QuickSort divides array.",
            "course_name": "CS301-Algorithms",
            "rubrics": [
                {
                    "question_num": 1,
                    "max_marks": 10.0,
                    "model_answer": "Hash table",
                    "key_concepts": ["hash table"],
                },
                {
                    "question_num": 2,
                    "max_marks": 10.0,
                    "model_answer": "QuickSort",
                    "key_concepts": ["quicksort"],
                },
            ],
        }
        res = await client.post("/api/v1/exam-workflow/process", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["run_id"] == "run_api_exam_001"
        assert data["status"] in ("completed", "requires_approval")
        assert "marks_awarded" in data
        assert "decision_hash" in data
        assert len(data["decision_hash"]) == 64


@pytest.mark.asyncio
async def test_exam_workflow_api_invalid_base64():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "run_id": "run_api_err",
            "file_base64": "NOT_VALID_BASE64_!!!",
        }
        res = await client.post("/api/v1/exam-workflow/process", json=payload)
        assert res.status_code == 400
