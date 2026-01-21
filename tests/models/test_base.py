from unittest.mock import patch

import pytest

from hope_live.models.base import BaseModel, BaseQuerySet


class ConcreteModel(BaseModel):
    class Meta:
        app_label = "hope_live"


def test_base_queryset_get_does_not_exist():
    # We need to mock the super().get() call to raise DoesNotExist
    with patch("django.db.models.QuerySet.get", side_effect=ConcreteModel.DoesNotExist):
        qs = BaseQuerySet(model=ConcreteModel)

        with pytest.raises(ConcreteModel.DoesNotExist) as exc:
            qs.get(id=1)

    assert "matching query does not exist" in str(exc.value)


def test_base_model_get_change_url():
    obj = ConcreteModel()
    obj.pk = 1

    with patch("hope_live.models.base.reverse") as mock_reverse:
        mock_reverse.return_value = "/url/"
        assert obj.get_change_url() == "/url/"
        mock_reverse.assert_called_with("workspace:hope_live_concretemodel_change", args=[1])
