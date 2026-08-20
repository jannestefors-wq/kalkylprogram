# House Engine Event Contract

Direktorder S24/S25. No House Engine code exists in any repository
accessible to this session; this contract is therefore speculative
scaffolding for a future integration, not a verified interface to a real
system.

## Principle

> Core Engine levererar betydelse. House Engine levererar upplevelse.

`adapters/house_engine_contract.py` defines `HouseEvent`: `event_type`
(one of `reflection_started`, `dimension_opened`, `deep_reflection`,
`tool_discovered`, `session_completed` -- exactly the five named in
Direktorder S24), `session_id`, `occurred_at`, and a free-form
`semantic_payload: dict[str, str]` for meaning-only key/value pairs (e.g.
`{"dimension": "trygghet"}`).

## Hard rule, enforced by test

`HouseEvent` must never gain a field describing color, light, brightness,
projection, CSS, or any other presentation property.
`tests/test_house_events_semantic_only.py` fails the build if a field name
containing any of `color, colour, css, light, brightness, projection, hue,
style` is added to the model. Translating semantic events into physical
effects is entirely House Engine's responsibility, whenever House Engine is
built.

## Status

Schema only, no emitter wired to any real session flow, no receiver built.
Direktorder S33 explicitly excludes changing lighting/projections in this
order.
