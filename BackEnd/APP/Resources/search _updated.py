from flask_restful import Resource, reqparse
from bson.objectid import ObjectId

# User-Defined Modules
from APP import Mongodb
from APP.config import Config
from APP.Resources import projection

class Search(Resource):
    # Argument Parser
    def _arguments(self, args: dict):
        print(args)
        print()
        and_filters = list()
        match = list()
        perfect_dict = dict()
        # Country filter
        if len(args.get('Country')) != 0:
            perfect_dict["Country"] = {$in:args.get('Country')}
        
        # State/Region filter
        if args.get('State/Region') != None and args.get('State/Region') != "":
            perfect_dict["State/Region"] = args.get('State/Region')

        # City filter
        if args.get('City') != None and args.get('City') != "":
            perfect_dict["City"] = args.get('City')
       
        #Category filter
        if args.get('category') != None and args.get('category') != "":
            perfect_dict["Industry"] = args.get('Industry')

        #jobtitle filter
        if args.get('jobtitle') != None and args.get('jobtitle') != "":
            perfect_dict["JobTitle"] = args.get('JobTitle')

        and_filters.append(perfect_dict)
        if(args.get('keyword')!=""):
            keyword = [
                {'JobTitle': "/"+args.get('keyword')+"/"},
                {'AssetName': "/"+args.get('keyword')+"/"},
                {'CampaignName': "/"+args.get('keyword')+"/"},
                {'CompanyName': "/"+args.get('keyword')+"/"},
                {'Industry': "/"+args.get('keyword')+"/"}
            ]
            and_filters.append('{$or':keyword})
        filters = dict()
        filters['$and':and_filters]
        return filters

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument(name='category', location='json', type=str)
        parser.add_argument(name='jobtitle', location='json', type=str)
        parser.add_argument(name='search_type', location='json', type=str, required=True)
        parser.add_argument(name='keyword', location='json', type=str, required=True)
        parser.add_argument(name='country', location='json', type=list, dest='Country')
        parser.add_argument(name='state', location='json', type=str, dest='State/Region')
        parser.add_argument(name='city', location='json', type=str, dest='City')

        parser.add_argument(name='employee', location='json', type=str)
        parser.add_argument(name='score', location='json', type=int)

        #page and limit being retrived from the url post method
        parser.add_argument(name='limit', location='args', type=int, required=True)
        parser.add_argument(name='page', location='args', type=int, required=True)
        args = parser.parse_args(strict=True)

        try:
            filters = self._arguments(args=args)
            rows = args.get('limit')
            page = args.get('page')
            print(filters)
            response = Mongodb.Aggregation([
                {'$match': filters},
                {'$skip': rows*(page-1) if page > 0 else 0},
                {'$limit': args.get('limit', 20)},
            ])
            result = dict()
            result['status'] = 'sucess'
            result['data'] = response
            result['count'] = len(output)
            return result, 200
        except Exception as e:
            result = dict()
            print ("\nError!!!\n",e)
            result['status'] = 'failure'
            result['message'] = 'InternalError'
            result['description'] = str(e)
            return result, 500