from __future__ import print_function
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import numpy as np


class HaversineRouteOptimizer:
    
    def __haversine(self, lon1, lat1, lon2, lat2):
        from math import radians, cos, sin, asin, sqrt

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radio de la tierra en km.

        return c * r
    
    def __build_distance_matrix(self, locations: list):
        num_locations = len(locations)
        distances = np.zeros((num_locations, num_locations))
        for idx1, l1 in enumerate(locations):
            for idx2, l2 in enumerate(locations):
                distances[idx1, idx2] = self.__haversine(l1[1], l1[0], l2[1], l2[0])

        return distances
    
    def __create_data_model(self, distances: list, origen: int, n_vehicles: int = 1):
        """Creates data structure with dimensions, num vehicles and the origin."""
        data = {}
        data["distance_matrix"] = distances
        data['num_locations'] = len(distances)
        data['num_vehicles'] = n_vehicles
        data['depot'] = origen
        return data

    def __get_distance_callback(self, data):
        """Creates callback to return distance between points."""

        distances = data['distances']
        def distance_callback(from_node, to_node):
            """Returns the manhattan distance between the two nodes"""
            return distances[from_node][to_node]
        return distance_callback
    
    def __print_solution(self, data, routing, assignment):
        """Print routes on console."""

        optimization_routes = []
        total_distance = 0
        for vehicle_id in range(data['num_vehicles']):
            vehicle_nodes = []
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_dist = 0
            while not routing.IsEnd(index):
                node_index = routing.IndexToNode(index)
                next_node_index = \
                    routing.IndexToNode(assignment.Value(routing.NextVar(index)))
                route_dist += routing.GetArcCostForVehicle(node_index,
                        next_node_index, vehicle_id)
                plan_output += ' {0} ->'.format(node_index)
                index = assignment.Value(routing.NextVar(index))
                vehicle_nodes.append(node_index)
            plan_output += ' {}\n'.format(routing.IndexToNode(index))
            plan_output += 'Distance of route: {} km\n'.format(route_dist)
            print(plan_output)
            total_distance += route_dist
            optimization_routes.append(vehicle_nodes)
        print('Total distance of all routes: {} km'.format(total_distance))
        return optimization_routes

    def __parse_solution(self, data, manager, routing, solution):
        """Prints solution on console."""
        max_route_distance = 0
        vehicles_plan = []
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            vehicle_route = {
                'id': vehicle_id,
                'steps': [],
                'distance': 0
            }
            route_distance = 0
            while not routing.IsEnd(index):
                vehicle_route['steps'].append(manager.IndexToNode(index))

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            
            vehicle_route['steps'].append(vehicle_route['steps'][0])
            vehicle_route['distance'] += route_distance
            vehicles_plan.append(vehicle_route)
        return vehicles_plan

    def __print_route_report(self, names, parsed_solution):
        total_distance = 0
        for vehicle_route in parsed_solution:
            print("Vehicle:{:>2}   Distance:{:>5}km   Route: {}".format(
                vehicle_route['id'],
                vehicle_route['distance'],
                str(list(map(lambda l: names[l], vehicle_route['steps'])))
                )
            )
            total_distance += vehicle_route['distance']
        print("Total distance: {}km".format(total_distance))

    def optimize(self, locations, names, origin, n_vehicles):
        print("Computing distance matrix...")
        distances = self.__build_distance_matrix(locations)

        print("Creating data model...")
        data = self.__create_data_model(distances, origin, n_vehicles = n_vehicles)

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                            data['num_vehicles'], data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            10000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        parsed_solution = self.__parse_solution(data, manager, routing, solution)
        print("Results: ")
        self.__print_route_report(names, parsed_solution)

        return parsed_solution