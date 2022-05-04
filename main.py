import os
from scraper_pcs.matchformats import spring_classics, grand_tour
from utility import result_objects

def main() -> None:
    
    if os.getenv('COMPETITION_NAME') == 'SpringClassics':
        spring_classics()
    else: 
        grand_tour()   




if __name__ == '__main__':
    # main()
    calculate_hundredpercentrule()

