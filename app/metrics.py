from typing import List, Dict


def calculate_accuracy(results):

    valid_results = [
        r for r in results
        if "expected_category" in r
        and "predicted_category" in r
    ]

    if not valid_results:
        return 0.0


    correct = 0


    for result in valid_results:

        if (
            result["expected_category"]
            ==
            result["predicted_category"]
        ):
            correct += 1


    return round(
        correct / len(valid_results) * 100,
        2
    )


def category_breakdown(results):

    categories = {}


    for result in results:

        if "expected_category" not in result:
            continue


        category = result["expected_category"]


        if category not in categories:

            categories[category] = {
                "total":0,
                "correct":0
            }


        categories[category]["total"] += 1


        if (
            result["expected_category"]
            ==
            result["predicted_category"]
        ):
            categories[category]["correct"] += 1



    for category in categories:

        data = categories[category]

        data["accuracy"] = round(
            data["correct"]
            /
            data["total"]
            *
            100,
            2
        )


    return categories