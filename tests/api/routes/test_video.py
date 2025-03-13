from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.dto.reddit_comment import ResponseMessage
from app.main import app

client = TestClient(app)


def test_add_comments_to_video(tmp_path):
    # Create a temporary test video file
    video_file = tmp_path / "test_video.mp4"
    video_file.write_bytes(b"fake video content")
    video_path = str(video_file)

    # Prepare request data
    comments_data = [
        {
            "username": "testuser",
            "text": "This is a test comment",
            "start_time": 1.0,
            "duration": 5.0
        }
    ]
    request_data = {
        "video_name": video_path,
        "comments": comments_data
    }

    # Mock the service response
    mock_output_path = "/path/to/output/video.mp4"
    mock_response = ResponseMessage(message="Comments added successfully", success=True)

    # Patch the service method
    with patch("app.services.video_service.VideoService.add_comments_to_video",
               return_value=mock_response) as mock_add_comments:

        # When: Making a POST request to the endpoint
        response = client.post("/api/video/add-reddit-comments/", json=request_data)

        # Then: Response should be successful
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] == True

        # Verify service was called with correct parameters
        mock_add_comments.assert_called_once()


def test_add_comments_to_video_file_not_found():
    # Given: A request with non-existent video path
    non_existent_path = "/path/to/nonexistent/video.mp4"
    comments_data = [
        {
            "username": "testuser",
            "text": "This is a test comment",
            "start_time": 1.0,
            "duration": 5.0
        }
    ]
    request_data = {
        "video_path": non_existent_path,
        "comments": comments_data
    }

    # When: Making a POST request to the endpoint
    response = client.post("/video/add-comments/", json=request_data)

    # Then: Response should be 404 Not Found
    assert response.status_code == 404
    response_data = response.json()
    assert "Video file not found" in response_data["detail"]