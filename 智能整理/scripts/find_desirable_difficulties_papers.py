import os
import glob

def find_desirable_difficulties_papers(root_dir, keywords):
    """
    Searches for markdown files in subdirectories of root_dir that contain 
    any of the specified keywords.

    Args:
        root_dir (str): The path to the root directory to search in.
        keywords (list): A list of keywords to search for.
    """
    found_papers = []
    for dirpath, _, filenames in os.walk(root_dir):
        md_files = [f for f in filenames if f.endswith('.md')]
        
        for md_file_name in md_files:
            md_file_path = os.path.join(dirpath, md_file_name)
            try:
                with open(md_file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in keywords):
                        if md_file_path not in found_papers:
                            found_papers.append(md_file_path)
            except Exception as e:
                print(f"Error reading {md_file_path}: {e}")
    
    if found_papers:
        print(f"\nFound {len(found_papers)} papers related to the keywords:")
        for paper in found_papers:
            print(paper)

        # Save the report to a file
        report_path = os.path.join(os.path.dirname(__file__), 'desirable_difficulties_report.txt')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Found {len(found_papers)} papers related to the keywords:\n\n")
                for paper in found_papers:
                    f.write(f"{paper}\n")
            print(f"\nReport successfully saved to: {report_path}")
        except Exception as e:
            print(f"\nError saving report: {e}")
            
    else:
        print("No papers found mentioning the specified keywords.")

if __name__ == "__main__":
    search_directory = '/Users/tommy/Projects/projects/AI学术分析/智能整理/data/raw/Rober_Bjork_MD_35'
    search_keywords = [
        "desirable difficulties",
        "retrieval strength",
        "storage strength",
        "testing effect",
        "spacing effect"
    ]
    print(f"Searching for papers with keywords in: {search_directory}")
    find_desirable_difficulties_papers(search_directory, search_keywords)
