import pytest

from pdf2aas.dictionary import PropertyDefinition
from pdf2aas.extractor import DummyPropertyLLM, CustomLLMClient, PropertyLLMOpenAI, Property

def test_dummy_property_llm_extract():
    e = DummyPropertyLLM()
    p = PropertyDefinition("EC002714")
    r = DummyPropertyLLM.empty_property_result(p)
    assert(e.extract("datasheet", p) == r)

example_property_definition1 = PropertyDefinition("p1", {'en': 'property1'}, 'numeric', {'en': 'definition of p1'}, 'T')
example_property_definition2 = PropertyDefinition("p2", {'en': 'property2'}, 'string', {'en': 'definition of p2'}, values=['a', 'b'])

example_property_value1 = Property('property1', 1, 'kT', 'p1 is 1Nm', example_property_definition1)
example_property_value2 = Property('property2', 'a', None, 'p2 is a', example_property_definition2)

example_accepted_llm_response = [
        '[{"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}]',
        '{"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}',
        '{"result": [{"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}]}',
        '{"property": [{"label": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}]}',
        '{"mykey": {"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}}',
        '{"property1": {"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}}',
        'My result is\n```json\n[{"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}]```',
    ]

example_accepted_llm_response_multiple = [
    '[{"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"},{"property": "property2", "value": "a", "unit": null, "reference": "p2 is a"}]',
    '{"property1": {"property": "property1", "value": 1, "unit": "kT", "reference": "p1 is 1Nm"}, "property2": {"property": "property2", "value": "a", "unit": null, "reference": "p2 is a"}}',
]

class DummyLLMClient(CustomLLMClient):
    def __init__(self) -> None:
        self.response = ""
        self.raw_response = ""
    def create_completions(self, messages: list[dict[str, str]], model: str, temperature: float, max_tokens: int, response_format: dict) -> tuple[str, str]:
        return self.response, self.raw_response

class TestPropertyLLMOpenAI():    
    llm = PropertyLLMOpenAI('test', client=DummyLLMClient())

    @pytest.mark.parametrize("response", example_accepted_llm_response)
    def test_propertyLLM_parse_accepted_llm_response(self, response):
        self.llm.client.response = response
        properties = self.llm.extract("datasheet", example_property_definition1)
        assert properties == [example_property_value1]
        properties = self.llm.extract("datasheet", [example_property_definition1])
        assert properties == [example_property_value1]
    
    def test_propertyLLM_parse_null_llm_response(self):
        self.llm.client.response = '{"property": null, "value": null, "unit": null, "reference": null}'
        properties = self.llm.extract("datasheet", example_property_definition1)
        assert properties == [Property('property1', None, None, None, example_property_definition1)]
    
    def test_propertyLLM_parse_accepted_incomplete_llm_response(self):
        self.llm.client.response = example_accepted_llm_response[0]
        properties = self.llm.extract("datasheet", [example_property_definition1, example_property_definition1])
        assert properties == [example_property_value1]
    
    @pytest.mark.parametrize("response", example_accepted_llm_response_multiple)
    def test_propertyLLM_parse_accepted_multiple_llm_response(self, response):
        self.llm.client.response = response
        properties = self.llm.extract("datasheet", [example_property_definition1, example_property_definition2])
        assert properties == [example_property_value1, example_property_value2]
    
    def test_propertyLLM_parse_accepted_multiple_incomplete_llm_response(self):
        self.llm.client.response = example_accepted_llm_response[0]
        properties = self.llm.extract("datasheet", [example_property_definition2, example_property_definition1])
        assert properties == [example_property_value1]
    
        