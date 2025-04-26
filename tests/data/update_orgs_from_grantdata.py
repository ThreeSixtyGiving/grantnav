import json
import sys
import argparse

# Example use:
# python3  ./update_orgs_from_grantdata.py --lookup-file ../../data/recipients.jl --entity-type recipient  a002400000KeYdsAAF-currency.json a002400000OiDBQAA3.json awefw001p00000zgyHZAAY.json grantnav-20180903134856.json  a002400000nO46WAAS.json > ./recipient.jsonl
# with the lookup-file comeing from the latest grant data package


def lookup_ids(json_files, entities_jsonl, entity_type):
    """
    Args:
        json_file_path (str): Path to the JSON file containing the grant data.
         (str): Path to the file to search for the IDs.

    Returns:
        dict: A dictionary where keys are the found IDs and values are lists of
              lines from the lookup file where the ID was found.
    """
    try:
        ids_to_lookup = set()
        for json_file_path in json_files:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)
                for item in data["grants"]:
                    try:
                        for org in item[entity_type]:
                            ids_to_lookup.add(org["id"])
                    except KeyError:
                        # could be grant to ind
                        continue

        with open(entities_jsonl, "r") as lookup_file:
            for line in lookup_file:
                org = json.loads(line)
                for id_val in ids_to_lookup:
                    if id_val in org["id"]:
                        print(line, end="")

    except FileNotFoundError:
        print("Error: One or both files not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file}'.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract IDs from JSON files and lookup in another file."
    )
    parser.add_argument(
        "json_files", nargs="+", help="One or more JSON files to process."
    )
    parser.add_argument(
        "--lookup-file", required=True, help="The file to search for the extracted IDs."
    )
    parser.add_argument(
        "--entity-type", required=True, help="The entity type (recipient/funder)."
    )

    args = parser.parse_args()

    if args.entity_type == "funder":
        entity_type = "fundingOrganization"
    elif args.entity_type == "recipient":
        entity_type = "recipientOrganization"
    else:
        print("Entity type must be valid organisation type (recipient/funder)")
        sys.exit(1)

    lookup_ids(args.json_files, args.lookup_file, entity_type)
