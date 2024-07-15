def load_coordinates(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    coordinates = []
    for line in lines:
        lon, lat = map(float, line.strip().split(','))
        coordinates.append((lon, lat))
    
    return coordinates

def calculate_effective_area(points):
    n = len(points)
    areas = []
    
    for i in range(1, n-1):
        x1, y1 = points[i-1]
        x2, y2 = points[i]
        x3, y3 = points[i+1]
        
        area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        areas.append(area)
    
    return areas

def visvalingam(points, num_points_to_keep):
    if len(points) <= num_points_to_keep:
        return points
    
    areas = calculate_effective_area(points)
    indexed_areas = list(enumerate(areas))
    indexed_areas.sort(key=lambda x: x[1], reverse=True)
    
    points_to_keep = set()
    for index, _ in indexed_areas[:num_points_to_keep]:
        points_to_keep.add(index)
    
    simplified_points = [points[i] for i in range(len(points)) if i in points_to_keep or i == 0 or i == len(points) - 1]
    
    return simplified_points

# File path to your path.txt
file_path = 'pathfile2.txt'


# Number of points to keep after simplification
num_points_to_keep = 25

# Load coordinates from file
coordinates = load_coordinates(file_path)

# Simplify using Visvalingam's algorithm
simplified_coordinates = visvalingam(coordinates, num_points_to_keep)

# Output the number of points in the simplified polyline
print(f'Number of points after simplification: {len(simplified_coordinates)}')
print(simplified_coordinates[:])  # Display the first 10 simplified coordinates

