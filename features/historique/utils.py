

from dotenv import load_dotenv
from typing import List
from features.uploads.models import Image

load_dotenv()


def format_result(results: List[dict]) -> List[str]:
    fruit_counts = {}

    for item in results:
        name = item["fruit_name"]
        quantity = item["quantity"]

        if name in fruit_counts:
            fruit_counts[name] += quantity
        else:
            fruit_counts[name] = quantity

    formatted_fruits = [f"{qty} {fruit}" for fruit,
                        qty in fruit_counts.items()]

    return ", ".join(formatted_fruits) + "."


def get_dict_result(results):
    results_data = []
    for r in results:
        info = {}
        info["quantity"] = r.split(",")[0]
        info["fruit_name"] = r.split(",")[-1]
        results_data.append(info)
    return results_data


def encode_image_results(images: list[Image]):
    result_dict = []
    for item in images:
        res: str = item.resultat
        results = res.split(";")
        info_dict = {}
        info_dict["img_id"] = str(item.id_image)
        info_dict["image_url"] = str(item.image_path)
        fruits = get_dict_result(results)
        info_dict["fruits"] = fruits
        result_dict.append(info_dict)
    return result_dict
