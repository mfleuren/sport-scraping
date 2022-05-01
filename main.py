import os
from scraper_pcs.matchformats import spring_classics, grand_tour

def main() -> None:
    
    if os.getenv('COMPETITION_NAME') == 'SpringClassics':
        spring_classics()
    else: 
        grand_tour()   


if __name__ == '__main__':
    main()