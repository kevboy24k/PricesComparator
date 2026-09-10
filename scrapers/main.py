import argparse, logging
from stores.kemik import KemikScraper
from stores.intelaf import IntelafScraper
from stores.pacifiko import PacifikoScraper
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
SCRAPERS={'kemik':KemikScraper,'intelaf':IntelafScraper,'pacifiko':PacifikoScraper}
if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('store',choices=SCRAPERS);parser.add_argument('query');args=parser.parse_args()
    logging.info('Ejecutando scraper %s para %s',args.store,args.query);print(SCRAPERS[args.store]().search(args.query))
