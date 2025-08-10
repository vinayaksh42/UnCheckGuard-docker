import json
import argparse

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def find_external_calls(client_methods, library_methods):
    external_calls = []
    library_method_signatures = {method['methodSignature'] for method in library_methods}

    for client_class in client_methods:
        for methods in client_class.values():
            for method in methods:
                if 'external_method_calls' in method:
                    for external_call in method['external_method_calls']:
                        if external_call in library_method_signatures:
                            external_calls.append({
                                'client_method': method['methodSignature'],
                                'external_call': external_call
                            })

    return external_calls

def main():
    parser = argparse.ArgumentParser(description='Process two library strings.')
    parser.add_argument('ClientJsonPath', type=str, help='path to the json of client')
    parser.add_argument('LibraryJsonPath', type=str, help='path to the json of library')
    parser.add_argument('OutputPath', type=str, help='path to the output json')
    args = parser.parse_args()

    client_methods = load_json(args.ClientJsonPath)
    library_methods = load_json(args.LibraryJsonPath)

    external_calls = find_external_calls(client_methods, library_methods)

    with open(('../CompareResult/' + args.OutputPath) , 'w') as output_file:
        json.dump(external_calls, output_file, indent=4)

if __name__ == '__main__':
    main()