import json
import re


class ASCParser:
    def __init__(self, asc_file_path):
        self.asc_file_path = asc_file_path
        self.components = []
        self.wires = []
        self.flags = []
        self.version = None
        self.sheet = None
        self.component_counter = 0
        
    def parse(self):
        """Parse the ASC file and convert it to a structured format"""
        with open(self.asc_file_path, 'r') as file:
            lines = file.readlines()
            
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith("Version"):
                self.version = line.split()[1]
                
            elif line.startswith("SHEET"):
                parts = line.split()
                self.sheet = {
                    "number": int(parts[1]),
                    "width": int(parts[2]),
                    "height": int(parts[3])
                }
                
            elif line.startswith("SYMBOL"):
                component = self._parse_symbol_line(line)
                # Look for associated SYMATTR lines
                i += 1
                while i < len(lines) and lines[i].strip().startswith("SYMATTR"):
                    attr_line = lines[i].strip()
                    self._add_symattr_to_component(component, attr_line)
                    i += 1
                i -= 1  # Adjust for the outer loop increment
                self.components.append(component)
                
            elif line.startswith("WIRE"):
                wire = self._parse_wire_line(line)
                self.wires.append(wire)
                
            elif line.startswith("FLAG"):
                flag = self._parse_flag_line(line)
                self.flags.append(flag)
                
            i += 1
            
        # Remove duplicates
        self._remove_duplicate_components()
        self._remove_duplicate_wires()
            
        return self._to_json()
    
    def _parse_symbol_line(self, line):
        """Parse a SYMBOL line and return a component dictionary"""
        parts = line.split()
        component_type = parts[1]
        x = int(parts[2])
        y = int(parts[3])
        rotation = parts[4]
        
        self.component_counter += 1
        
        return {
            "id": f"comp_{self.component_counter}",
            "type": component_type,
            "x": x,
            "y": y,
            "rotation": rotation,
            "attributes": {}
        }
    
    def _add_symattr_to_component(self, component, line):
        """Add SYMATTR attributes to a component"""
        parts = line.split()
        attr_type = parts[1]
        attr_value = " ".join(parts[2:]) if len(parts) > 2 else ""
        
        if attr_type == "InstName":
            component["attributes"]["name"] = attr_value
        else:
            component["attributes"][attr_type] = attr_value
    
    def _parse_wire_line(self, line):
        """Parse a WIRE line and return a wire dictionary"""
        parts = line.split()
        x1 = int(parts[1])
        y1 = int(parts[2])
        x2 = int(parts[3])
        y2 = int(parts[4])
        
        return {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
    
    def _parse_flag_line(self, line):
        """Parse a FLAG line and return a flag dictionary"""
        parts = line.split()
        x = int(parts[1])
        y = int(parts[2])
        net_name = parts[3]
        
        return {
            "x": x,
            "y": y,
            "net_name": net_name
        }
    
    def _remove_duplicate_components(self):
        """Remove duplicate components based on position, type and attributes"""
        unique_components = []
        seen_components = set()
        
        for component in self.components:
            # Create a unique key based on component properties
            key = (component["type"], component["x"], component["y"], component["rotation"],
                   component["attributes"].get("name", ""))
            
            if key not in seen_components:
                seen_components.add(key)
                unique_components.append(component)
        
        self.components = unique_components
    
    def _remove_duplicate_wires(self):
        """Remove duplicate wires based on coordinates"""
        unique_wires = []
        seen_wires = set()
        
        for wire in self.wires:
            # Create a unique key based on wire coordinates
            # Normalize the wire representation (start point should be min of the two points)
            x1, y1 = min((wire["x1"], wire["y1"]), (wire["x2"], wire["y2"]))
            x2, y2 = max((wire["x1"], wire["y1"]), (wire["x2"], wire["y2"]))
            key = (x1, y1, x2, y2)
            
            if key not in seen_wires:
                seen_wires.add(key)
                unique_wires.append(wire)
        
        self.wires = unique_wires
    
    def _to_json(self):
        """Convert parsed data to JSON format"""
        circuit_data = {
            "version": self.version,
            "sheet": self.sheet,
            "components": self.components,
            "wires": self.wires,
            "flags": self.flags
        }
        
        return circuit_data
    
    def save_json(self, output_path):
        """Parse the ASC file and save as JSON"""
        circuit_data = self.parse()
        with open(output_path, 'w') as json_file:
            json.dump(circuit_data, json_file, indent=2)
        return circuit_data


def convert_asc_to_json(asc_file_path, json_file_path=None):
    """
    Convert an LTspice ASC file to JSON format
    
    Args:
        asc_file_path (str): Path to the input ASC file
        json_file_path (str, optional): Path to save the output JSON file.
                                       If None, returns the JSON data without saving.
    
    Returns:
        dict: The circuit data in JSON format
    """
    parser = ASCParser(asc_file_path)
    circuit_data = parser.parse()
    
    if json_file_path:
        parser.save_json(json_file_path)
        
    return circuit_data


# Example usage
if __name__ == "__main__":
    # Convert ltspice_final.asc to JSON
    circuit_data = convert_asc_to_json("ltspice_final.asc", "circuit_output.json")
    print("Conversion completed. Circuit data:")
    print(json.dumps(circuit_data, indent=2))