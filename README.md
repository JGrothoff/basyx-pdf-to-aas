# PDF to AAS

Python libraries and scripts to extract technical data from PDFs utilizing Transformers and especially **Large Language Models (LLMs)** to format them in an **Asset Administration Shell (AAS)** submodel.

## Workflow

```mermaid
flowchart LR
    dataSheet[Data Sheet]
    dictionary[("Property 
                 Dictionary")]
    llm{{LLM}}
    submodel[AAS Submodel]

    preprocessor[[PDF Preprocessor]]
    propertyPreprocessor[[Property Preprocessor]]
    propertyExtractor[[Extractor]]
    submodelGenerator[[Generator]]

    dataSheet --pdf---> preprocessor --text--> propertyExtractor

    dataSheet -.classification.-> propertyPreprocessor
    dictionary --"class and
    property definition"---> propertyPreprocessor --"property 
        definitions"
        -->  propertyExtractor

    propertyExtractor --prompt--> llm --property--> propertyExtractor
    propertyExtractor --property list--> submodelGenerator

    submodelGenerator --json--> submodel
```

## Modules

* **preprocessor**: converts the PDF to a text format that can be processed by LLMs, keeping layout and table information.
  * **pdf2html**: Uses [pdf2htmlEX](https://github.com/pdf2htmlEX/pdf2htmlEX) to convert the PDF data sheets to HTML.
    The converted html is preprocessed further to reduce token usage for the llms.
* **dictionary**: defines classes and properties semantically.
  * **eclass**: downloads eclass property definitions with value lists etc. from [eclass website](https://eclass.eu/en/eclass-standard/search-content) for a given eclass class.
* **extractor**: extracts technical properties from the preprocessed data sheet.
  * **propertyLLM**: Uses an LLM to search and extract a single property value with its unit from the given text.
* **generator**: transforms a given property-value list into different formats.
  * **submodelTD**: outputs the properties in a [technical data submodel](https://github.com/admin-shell-io/submodel-templates/tree/main/published/Technical_Data/1/2).

## run tests

* Install `pytest` package
* cd into `pdf2aas/pdf2aas`
* Run tests with `python -m pytest`
