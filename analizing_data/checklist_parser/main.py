import os
from excel_parser import ExcelChecklistParser
from metadata_extractor import MetadataExtractor
from structure_parser import ExcelStructureParser
import json

if __name__ == "__main__":
    parser = ExcelChecklistParser(MetadataExtractor(), ExcelStructureParser())
    files = [
        "data/form1.xlsx",
        "data/form2.xlsx",
        "data/form3.xlsx",
        "data/form4.xlsx",
        "data/form5.xlsx",
        "data/form6.xlsx",
    ]

    os.makedirs("output", exist_ok=True)
    for f in files:
        try:
            result = parser.parse_file(f)
            output_file = os.path.join("output", os.path.basename(f).replace(".xlsx", ".json"))
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(result, json_file, indent=2, ensure_ascii=False)
            print(f"Результат для {f} сохранён в {output_file}")
        except Exception as e:
            print(f"Ошибка в {f}: {e}")