from typing import Any

import pytest

from src.application.ports.usecases import IndexAdPort, RemoveAdPort
from src.application.services.kafka_ads_consumer import KafkaAdsConsumer
from src.tracing import get_trace_id


class _Msg:
    def __init__(self, value: dict[str, Any]) -> None:
        self.value = value
        self.headers: list[tuple[str, bytes]] = []


class FakeConsumer:
    def __init__(self, messages: list[_Msg]) -> None:
        self._messages = messages
        self.commits = 0

    def __aiter__(self) -> "FakeConsumer":
        self._it = iter(self._messages)
        return self

    async def __anext__(self) -> _Msg:
        try:
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration

    async def commit(self) -> None:
        self.commits += 1


class RecordingIndexAd(IndexAdPort):
    def __init__(self) -> None:
        self.calls: list[tuple[int, str | None]] = []

    async def execute(self, ad_id: int) -> None:
        self.calls.append((ad_id, get_trace_id()))


class RecordingRemoveAd(RemoveAdPort):
    def __init__(self) -> None:
        self.calls: list[tuple[int, str | None]] = []

    async def execute(self, ad_id: int) -> None:
        self.calls.append((ad_id, get_trace_id()))


@pytest.mark.asyncio
async def test_consumer_binds_trace_id_from_envelope() -> None:
    index_ad = RecordingIndexAd()
    remove_ad = RecordingRemoveAd()
    consumer = FakeConsumer(
        [_Msg({"event": "ad.created", "trace_id": "t-42", "payload": {"ad_id": 5}})]
    )

    await KafkaAdsConsumer(consumer, index_ad, remove_ad).run()

    assert index_ad.calls == [(5, "t-42")]
    assert consumer.commits == 1
    assert get_trace_id() is None


@pytest.mark.asyncio
async def test_consumer_without_trace_id_binds_none() -> None:
    index_ad = RecordingIndexAd()
    remove_ad = RecordingRemoveAd()
    consumer = FakeConsumer([_Msg({"event": "ad.updated", "payload": {"ad_id": 9}})])

    await KafkaAdsConsumer(consumer, index_ad, remove_ad).run()

    assert index_ad.calls == [(9, None)]


@pytest.mark.asyncio
async def test_consumer_routes_delete_with_trace_id() -> None:
    index_ad = RecordingIndexAd()
    remove_ad = RecordingRemoveAd()
    consumer = FakeConsumer(
        [_Msg({"event": "ad.deleted", "trace_id": "t-7", "payload": {"ad_id": 3}})]
    )

    await KafkaAdsConsumer(consumer, index_ad, remove_ad).run()

    assert index_ad.calls == []
    assert remove_ad.calls == [(3, "t-7")]
    assert consumer.commits == 1
