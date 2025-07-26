import os
import tempfile
import torch
import cv2 as cv
import math
import numpy as np
import pandas as pd
import logging
import time
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.core.logging import get_logger
from app.services.asc_parser import ASCParsingService

logger = get_logger(__name__)

# Class that has wires as object with coordinates as attributes
class Wire:
    def __init__(self, x1, y1, x2, y2):
        if self.select_starting_point(x1, y1, x2, y2) == 1:
            self.x_start = x1
            self.y_start = y1
            self.x_end = x2
            self.y_end = y2
        else:
            self.x_start = x2
            self.y_start = y2
            self.x_end = x1
            self.y_end = y1
        # method for defining if the wire is horizontal or vertical
        self.orientation = self.test_if_wire_is_valid()
        # translation
        self.x_trans = None
        self.y_trans = None

    # using the formula for the slope between two points we get either vertical, horizontal or other
    # limit for the slope can be manually set
    def test_if_wire_is_valid(self):
        slope_as_angle = math.degrees(math.atan2((self.y_start - self.y_end), (self.x_start - self.x_end))) % 360
        limit = 10
        if (not limit < slope_as_angle <= 360 - limit) or (180 - limit <= slope_as_angle < 180 + limit):
            return "h"
        elif (90 - limit < slope_as_angle < 90 + limit) or (270 - limit < slope_as_angle < 270 + limit):
            return "v"
        return "o"
    
    # method for determining which point of the given wire is closer to the origin, then set it to the starting point
    def select_starting_point(self, x1, y1, x2, y2):
        # point closer to origin
        # origin is (0, 0)
        if np.sqrt(x1**2 + y1**2) < np.sqrt(x2**2 + y2**2):
            return 1
        else:
            return 2

    def straighten_wires(self):
        # straightens the wire
        if self.orientation == "h":
            self.y_end = self.y_start
        elif self.orientation == "v":
            self.x_end = self.x_start


class CircuitRecognitionService:
    def __init__(self):
        """
        Initialize the CircuitRecognitionService with the YOLOv5 model
        """
        logger.info("Initializing CircuitRecognitionService")
        try:
            self.model = torch.hub.load(
                settings.YOLOV5_PATH, 
                'custom',
                path=settings.MODEL_PATH, 
                source='local', 
                force_reload=True
            )
            logger.info("YOLOv5 model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading YOLOv5 model: {str(e)}")
            raise

    def process_image(self, file_content: bytes, output_format: str = "asc") -> Dict[str, Any]:
        """
        Process an image of a hand-drawn circuit and generate ASC or JSON output
        
        Args:
            file_content (bytes): The image file content as bytes
            output_format (str): The output format, either "asc" or "json"
            
        Returns:
            Dict[str, Any]: The processed circuit data in the requested format
            
        Raises:
            Exception: If there's an error processing the image
        """
        start_time = time.time()
        logger.info(f"Processing image with output format: {output_format}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Process the image using the refactored logic from beta_version.py
            logger.debug(f"Processing image at {temp_file_path}")
            asc_content = self._process_image_to_asc(temp_file_path)
            
            if output_format == "json":
                # Convert ASC to JSON using existing parser
                logger.debug("Converting ASC to JSON")
                json_data = ASCParsingService.convert_to_json(asc_content.encode())
                processing_time = time.time() - start_time
                logger.info(f"Image processing completed in {processing_time:.2f} seconds")
                return {"format": "json", "data": json_data, "processing_time": processing_time}
            else:
                processing_time = time.time() - start_time
                logger.info(f"Image processing completed in {processing_time:.2f} seconds")
                return {"format": "asc", "data": asc_content, "processing_time": processing_time}
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Temporary file {temp_file_path} cleaned up")

    def _process_image_to_asc(self, image_path: str) -> str:
        """
        Process an image and generate ASC file content
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: ASC file content as string
        """
        logger.info("Processing image to ASC format")
        
        # Load image and run inference
        img = cv.imread(image_path)[..., ::-1]  # image loader
        results = self.model(img, size=640)  # inference
        
        # Get results as pandas dataframes
        df = results.pandas().xywh[0]
        dfxyxy = results.pandas().xyxy[0]
        logger.debug(f"Detected {len(df)} objects in the image")
        
        # Process data for different component types
        data_ind = df.loc[df['name'] == 'inductor']
        data_gnd = df.loc[df['name'] == 'gnd']
        data_cap = df.loc[df['name'] == 'capacitor-unpolarized']
        data_vol_ac = df.loc[df['name'] == 'voltage-dc_ac']
        data_vol = df.loc[df['name'] == 'voltage-dc']
        data_res = df.loc[df['name'] == 'resistor']
        data = df.loc[df['name'] == 'junction']
        
        # Process junctions to align them to grid
        wires, wires_horizontal, wires_vertical = self._process_junctions(data)
        
        # Generate ASC content
        asc_content = self._generate_asc_content(
            data_res, data_vol, data_vol_ac, data_cap, data_gnd, data_ind, 
            wires, wires_horizontal, wires_vertical
        )
        
        logger.info("ASC content generated successfully")
        return asc_content

    def _process_junctions(self, data: pd.DataFrame) -> Tuple[List[Wire], List[Wire], List[Wire]]:
        """
        Process junction data to create wires
        
        Args:
            data (pd.DataFrame): DataFrame with junction data
            
        Returns:
            Tuple[List[Wire], List[Wire], List[Wire]]: All wires, horizontal wires, vertical wires
        """
        logger.debug("Processing junctions")
        
        # Align junctions
        for index, row in data.iterrows():
            align_x = []  # empty list containing x_coordinates that need to have the same value
            align_y = []  # empty list containing y_coordinates that need to have the same value

            for index2, row2 in data.iterrows():
                if index == index2:  # skip the same point
                    continue
                if abs(row["xcenter"]-row2["xcenter"]) < 50:  # taking two different points and append if they are close
                    align_x.append(index)  # appending the index of a valid coordinate for easier manipulation of the dataframe
                    align_x.append(index2)  # appending the index of a second valid coordinate...

                elif abs(row["ycenter"]-row2["ycenter"]) < 50:  # taking two different points and
                    # if they are close --> append in list
                    align_y.append(index)  # appending the index of a valid coordinate for easier manipulation of the dataframe
                    align_y.append(index2)  # appending the index of a second valid coordinate...

            # Iterating over the list
            for index in align_x:
                data.loc[index, "xcenter"] = data.loc[align_x[0], "xcenter"]  # equating every element of the list to the first

            # Iterating over the second list
            for index in align_y:
                data.loc[index, "ycenter"] = data.loc[align_y[0], "ycenter"]  # equating every element of the list to the first

        # Process of translating points to the 16x16 grid for ltspice, x_center
        for index, row in data.iterrows():
            if (data.loc[index, "xcenter"]) % 16 == 0:
                continue
            else:
                temp_x = row["xcenter"] % 16
                data.loc[index, "xcenter"] = row["xcenter"] - temp_x

        # Process of translating points to the 16x16 grid for ltspice, y_center
        for index, row in data.iterrows():
            if (data.loc[index, "ycenter"]) % 16 == 0:
                continue
            else:
                temp_y = row["ycenter"] % 16
                data.loc[index, "ycenter"] = row["ycenter"] - temp_y

        # Iterating over all of the junctions (now aligned junctions)
        wires = []
        checked_coordinates = []
        wires_horizontal = []
        wires_vertical = []
        
        for index, row in data.iterrows():
            for index2, row2 in data.iterrows():
                if (index, index2) in checked_coordinates or (index2, index) in checked_coordinates:  # condition to stop
                    # duplication caused by the iteration
                    continue
                checked_coordinates.append((index, index2))
                checked_coordinates.append((index2, index))
                # calling the class Wire and making each wire an object
                wire = Wire(
                    x1=int(row["xcenter"]),
                    y1=int(row["ycenter"]),
                    x2=int(row2["xcenter"]),
                    y2=int(row2["ycenter"])
                )
                if index == index2:
                    continue
                if wire.orientation == "o":
                    continue
                elif wire.orientation == "h":
                    wires_horizontal.append(wire)
                    wires.append(wire)  # appending horizontal wires
                elif wire.orientation == "v":
                    wires_vertical.append(wire)
                    wires.append(wire)  # appending vertical wires
                    
        logger.debug(f"Processed {len(wires)} wires from junctions")
        return wires, wires_horizontal, wires_vertical

    def _generate_asc_content(self, data_res: pd.DataFrame, data_vol: pd.DataFrame, 
                              data_vol_ac: pd.DataFrame, data_cap: pd.DataFrame, 
                              data_gnd: pd.DataFrame, data_ind: pd.DataFrame,
                              wires: List[Wire], wires_horizontal: List[Wire], 
                              wires_vertical: List[Wire]) -> str:
        """
        Generate ASC file content from processed data
        
        Returns:
            str: ASC file content as string
        """
        logger.debug("Generating ASC content")
        
        # Start building ASC content
        asc_lines = []
        asc_lines.append("Version 4")
        asc_lines.append("SHEET 1 880 680")
        
        # Process resistors
        counter = 1
        for index, row in data_res.iterrows():  # iterate over resistors
            for wire in wires:  # iterate over wire object
                if wire in wires_vertical:
                    if wire.y_start < row["ycenter"] < wire.y_end and wire.x_start - 35 < row["xcenter"] < wire.x_end + 35:
                        # proximity of the resistor to the wire condition
                        data_res.loc[index, "xcenter"] = wire.x_start - 16
                        # let the new x_center be the same as the x_start value of the wire,- 16 is to match the grid
                        text1 = "SYMBOL res {} {} R0\nSYMATTR InstName R{}\n".format(
                            int(data_res.loc[index, "xcenter"]), int(row["ycenter"]), counter)
                        asc_lines.append(text1)
                        counter = counter + 1  # counter increment

                elif wire in wires_horizontal:
                    if wire.x_start < row["xcenter"] < wire.x_end and wire.y_start - 35 < row["ycenter"] < wire.y_end + 35:
                        # proximity of the resistor to the wire condition
                        data_res.loc[index, "ycenter"] = wire.y_start - 16
                        # let the new y_center be the same as the y_start value of the wire,- 16 is to match the grid
                        text2 = "SYMBOL res {} {} R90\nSYMATTR InstName R{}\n".format(
                            int(row["xcenter"]), int(data_res.loc[index, "ycenter"]), counter)
                        asc_lines.append(text2)
                        counter = counter + 1  # counter increment
                else:
                    continue

        # Process voltage-dc sources
        counter = 1
        for index, row in data_vol.iterrows():  # iterate over voltage-dc sources
            for wire in wires:  # iterate over wire object
                if wire in wires_vertical:
                    if wire.y_start < row["ycenter"] < wire.y_end and wire.x_start - 25 < row["xcenter"] < wire.x_end + 25:
                        # proximity of the voltage-dc source to the wire
                        data_vol.loc[index, "xcenter"] = wire.x_start
                        # let the new x_center be the same as the x_start value of the wire,- 16 is to match the grid
                        text1 = "SYMBOL voltage {} {} R0\nSYMATTR InstName V{}\n".format(
                            int(data_vol.loc[index, "xcenter"]), int(row["ycenter"]) - 96, counter)
                        asc_lines.append(text1)
                        counter = counter + 1  # counter increment

                elif wire in wires_horizontal:
                    if wire.x_start < row["xcenter"] < wire.x_end and wire.y_start - 25 < row["ycenter"] < wire.y_end + 25:
                        # proximity of the voltage-dc source to the wire
                        data_vol.loc[index, "ycenter"] = wire.y_start
                        # let the new y_center be the same as the y_start value of the wire,- 16 is to match the grid
                        text2 = "SYMBOL voltage {} {} R270\nSYMATTR InstName V{}\n".format(
                            int(row["xcenter"]) - 96, int(data_vol.loc[index, "ycenter"]), counter)
                        asc_lines.append(text2)
                        counter = counter + 1  # counter increment
                else:
                    continue

        # Process voltage-dc_ac sources
        counter = 1
        for index, row in data_vol_ac.iterrows():  # iterate over voltage-dc_ac sources
            for wire in wires:  # iterate over wire object
                if wire in wires_vertical:
                    if wire.y_start < row["ycenter"] < wire.y_end and wire.x_start - 25 < row["xcenter"] < wire.x_end + 25:
                        # proximity of the voltage-dc_ac source to the wire
                        data_vol_ac.loc[index, "xcenter"] = wire.x_start
                        text1 = "SYMBOL voltage {} {} R0\nSYMATTR InstName V{}\n".format(
                            int(data_vol_ac.loc[index, "xcenter"]), int(row["ycenter"]) - 96, counter)
                        asc_lines.append(text1)
                        counter = counter + 1  # counter increment

                elif wire in wires_horizontal:
                    if wire.x_start < row["xcenter"] < wire.x_end and wire.y_start - 25 < row["ycenter"] < wire.y_end + 25:
                        # proximity of the voltage-dc_ac source to the wire
                        data_vol_ac.loc[index, "ycenter"] = wire.y_start
                        text2 = "SYMBOL voltage {} {} R270\nSYMATTR InstName V{}\n".format(
                            int(row["xcenter"]) - 96, int(data_vol_ac.loc[index, "ycenter"]), counter)
                        asc_lines.append(text2)
                        counter = counter + 1  # counter increment
                else:
                    continue

        # Process capacitors
        counter = 1
        for index, row in data_cap.iterrows():  # iterate over capacitor sources
            for wire in wires:  # iterate over wire object
                if wire in wires_vertical:
                    if wire.y_start < row["ycenter"] < wire.y_end and wire.x_start - 50 < row["xcenter"] < wire.x_end + 50:
                        # proximity of the voltage-dc source to the wire
                        data_cap.loc[index, "xcenter"] = wire.x_start - 16
                        # let the new x_center be the same as the x_start value of the wire,- 16 is to match the grid
                        text1 = "SYMBOL cap {} {} R0\nSYMATTR InstName C{}\n".format(
                            int(data_cap.loc[index, "xcenter"]), int(row["ycenter"]), counter)
                        asc_lines.append(text1)
                        counter = counter + 1  # counter increment

                elif wire in wires_horizontal:
                    if wire.x_start < row["xcenter"] < wire.x_end and wire.y_start - 25 < row["ycenter"] < wire.y_end + 25:
                        # proximity of the voltage-dc source to the wire
                        data_cap.loc[index, "ycenter"] = wire.y_start - 16
                        # let the new y_center be the same as the y_start value of the wire,- 16 is to match the grid
                        text2 = "SYMBOL cap {} {} R90\nSYMATTR InstName C{}\n".format(
                            int(row["xcenter"]), int(data_cap.loc[index, "ycenter"]), counter)
                        asc_lines.append(text2)
                        counter = counter + 1  # counter increment
                else:
                    continue

        # Process ground
        for index, row in data_gnd.iterrows():  # iterate over ground
            for wire in wires:  # iterate over wire object
                if wire in wires_horizontal:
                    if wire.x_start < row["xcenter"] < wire.x_end and wire.y_start - 200 < row["ycenter"] < wire.y_end + 200:
                        # proximity of the resistor to the wire condition
                        data_gnd.loc[index, "ycenter"] = wire.y_start + 16
                        # let the new y_center be the same as the y_start value of the wire,- 16 is to match the grid
                        text2 = "FLAG {} {} 0\n".format(int(row["xcenter"]), int(data_gnd.loc[index, "ycenter"]))
                        asc_lines.append(text2)
                        text2 = "WIRE {} {} {} {}\n".format(
                            int(row["xcenter"]), int(data_gnd.loc[index, "y_center"] - 16),
                            int(row["xcenter"]), int(data_gnd.loc[index, "ycenter"]))
                        asc_lines.append(text2)
                else:
                    continue

        # Process inductors
        counter = 1  # counter for unique names of the elements
        for index, row in data_ind.iterrows():  # iterate over inductors
            for wire in wires:  # iterate over wire object
                if wire in wires_vertical:
                    if wire.y_start < row["ycenter"] < wire.y_end and wire.x_start - 35 < row["xcenter"] < wire.x_end + 35:
                        # proximity of the resistor to the wire condition
                        data_ind.loc[index, "xcenter"] = wire.x_start - 16
                        # let the new x_center be the same as the x_start value of the wire,- 16 is to match the grid
                        text1 = "SYMBOL ind {} {} R0\nSYMATTR InstName L{}\n".format(
                            int(data_ind.loc[index, "xcenter"]), int(row["ycenter"]), counter)
                        asc_lines.append(text1)
                        counter = counter + 1  # counter increment

                elif wire in wires_horizontal:
                    if wire.x_start < row["xcenter"] < wire.x_end and wire.y_start - 35 < row["ycenter"] < wire.y_end + 35:
                        # proximity of the resistor to the wire condition
                        data_ind.loc[index, "ycenter"] = wire.y_start - 16
                        # let the new y_center be the same as the y_start value of the wire,- 16 is to match the grid
                        text2 = "SYMBOL ind {} {} R90\nSYMATTR InstName L{}\n".format(
                            int(row["xcenter"]), int(data_ind.loc[index, "ycenter"]), counter)
                        asc_lines.append(text2)
                        counter = counter + 1  # counter increment
                else:
                    continue

        # Add wires
        for wire in wires:
            text = f"WIRE {wire.x_start} {wire.y_start} {wire.x_end} {wire.y_end}\n"
            asc_lines.append(text)
            
        # Remove duplicates
        no_duplicates = list()
        for object in asc_lines:
            if object not in no_duplicates:
                no_duplicates.append(object)
                
        # Join all lines
        asc_content = "".join(no_duplicates)
        logger.debug(f"Generated ASC content with {len(no_duplicates)} lines")
        return asc_content