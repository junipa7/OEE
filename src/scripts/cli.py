import argparse

def main():
    parser = argparse.ArgumentParser(description="Auto_ST Command Line Interface")
    
    # Add command line arguments here
    parser.add_argument('--example', type=str, help='An example argument for demonstration purposes')
    
    args = parser.parse_args()
    
    # Handle the arguments and call the appropriate functions from the application
    if args.example:
        print(f'Example argument received: {args.example}')
    else:
        print('No example argument provided.')

if __name__ == "__main__":
    main()