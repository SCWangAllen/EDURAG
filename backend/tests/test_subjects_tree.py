from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import subjects
from app.routers.mock_subjects import router as mock_subjects_router
from app.services.subject_service import build_subject_tree


def _row(sid, name, grade, color="#3B82F6"):
    return SimpleNamespace(id=sid, name=name, grade=grade, color=color)


class TestBuildSubjectTree:
    def test_groups_rows_by_subject_name(self):
        tree = build_subject_tree(
            [
                _row(1, "health", "ALL"),
                _row(2, "health", "G4"),
                _row(3, "english", "ALL"),
            ]
        )
        assert [n["name"] for n in tree] == ["english", "health"]
        health = next(n for n in tree if n["name"] == "health")
        assert len(health["grades"]) == 2

    def test_all_grade_sorted_first_then_g1_to_g6(self):
        tree = build_subject_tree(
            [
                _row(1, "health", "G6"),
                _row(2, "health", "G1"),
                _row(3, "health", "ALL"),
            ]
        )
        grades = [g["grade"] for g in tree[0]["grades"]]
        assert grades == ["ALL", "G1", "G6"]

    def test_custom_grade_sorted_last(self):
        tree = build_subject_tree(
            [
                _row(1, "health", "初級"),
                _row(2, "health", "G2"),
            ]
        )
        grades = [g["grade"] for g in tree[0]["grades"]]
        assert grades == ["G2", "初級"]

    def test_color_taken_from_first_row(self):
        tree = build_subject_tree(
            [
                _row(1, "health", "ALL", color="#10B981"),
                _row(2, "health", "G4", color="#FFFFFF"),
            ]
        )
        assert tree[0]["color"] == "#10B981"

    def test_none_grade_becomes_empty_string(self):
        tree = build_subject_tree([_row(1, "health", None)])
        assert tree[0]["grades"][0]["grade"] == ""

    def test_grade_entries_keep_row_id(self):
        tree = build_subject_tree([_row(7, "health", "G4")])
        assert tree[0]["grades"][0]["id"] == 7


class TestTreeRouteOrdering:
    def test_tree_route_registered_before_subject_id(self):
        """/tree 必須排在 /{subject_id}（int 轉換器）之前，否則會被吃掉回 422"""
        paths = [route.path for route in subjects.router.routes]
        assert paths.index("/api/subjects/tree") < paths.index(
            "/api/subjects/{subject_id}"
        )


class TestMockSubjectsEndpoint:
    def setup_method(self):
        app = FastAPI()
        app.include_router(mock_subjects_router)
        self.client = TestClient(app)

    def test_tree_endpoint_returns_grouped_tree(self):
        response = self.client.get("/api/subjects/tree")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == len(data["subjects"])
        health = next(n for n in data["subjects"] if n["name"] == "health")
        assert [g["grade"] for g in health["grades"]] == ["ALL", "G4"]
        assert health["color"] == "#10B981"

    def test_list_endpoint_matches_real_schema(self):
        response = self.client.get("/api/subjects/")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == len(data["subjects"])
        first = data["subjects"][0]
        for key in ("id", "name", "grade", "color", "is_active"):
            assert key in first
