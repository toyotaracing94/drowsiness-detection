# Reference : https://hailo.ai/developer-zone/documentation/dataflow-compiler-v3-26-0/?sp_referrer=tutorials_notebooks/notebooks/DFC_4_Inference_Tutorial.html
from typing import List

import numpy as np
from hailo_platform import (
    HEF,
    ConfigureParams,
    FormatType,
    HailoStreamInterface,
    InferVStreams,
    InputVStreamParams,
    OutputVStreamParams,
    VDevice,
)

from backend.utils.logging import logging_default


class HailoInferenceEngine():
    def __init__(self):
        """
        Initialize the HailoInference class
        """
        # The target can be used as a context manager ("with" statement) 
        # to ensure it's released on time.
        self.target = VDevice()
        self.hef_cnt = 0
        self.hef_list = []
        self.network_group_list = []
        self.network_group_params_list = []
        self.input_vstreams_params_list = []
        self.output_vstreams_params_list = []
        self.input_vstream_info_list = []
        self.output_vstream_info_list = []
    
    def load_model(self, hef_path : str):
        """
        Initialize the HailoInference class with the provided HEF model file path.

        Parameters
        ----------
        hef_path: str 
            Path to the HEF model file.
        """
        hef_id = self.hef_cnt
        hef = HEF(hef_path)
        network_group = self._configure_and_get_network_group(hef, self.target)
        network_group_params = network_group.create_params()
        input_vstreams_params, output_vstreams_params = self._create_vstream_params(network_group)
        self.input_vstream_info, self.output_vstream_info = self._get_and_print_vstream_info(hef)
        
        self.hef_list.append(hef)
        self.network_group_list.append(network_group)
        self.network_group_params_list.append(network_group_params)
        self.input_vstreams_params_list.append(input_vstreams_params)
        self.output_vstreams_params_list.append(output_vstreams_params)
        self.input_vstream_info_list.append(self.input_vstream_info)
        self.output_vstream_info_list.append(self.output_vstream_info)

        self.hef_cnt += 1

        return hef_id

    def _configure_and_get_network_group(self, hef : HEF, target : VDevice):
        """
        Configure the Hailo device and get the network group.

        Parameters
        ----------
        hef: HEF 
            HEF model object.
        target : VDevice
            Hailo device target.

        Returns
        ----------
        NetworkGroup: 
            Configured network group.
        """
        configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
        network_group = target.configure(hef, configure_params)[0]
        return network_group
    
    def _create_vstream_params(self, network_group):
        """
        Create input and output stream parameters.

        Parameters
        ----------
        network_group: NetworkGroup
            Configured network group.

        Returns
        ----------
        Tuple: 
            (InputVStreamParams, OutputVStreamParams): Input and output stream parameters.
        """
        input_vstreams_params = InputVStreamParams.make_from_network_group(network_group)
        output_vstreams_params = OutputVStreamParams.make_from_network_group(network_group, format_type=FormatType.FLOAT32)
        return input_vstreams_params, output_vstreams_params
    
    def _get_and_print_vstream_info(self, hef : HEF):
        """
        Get and print information about input and output stream layers.

        Parameters
        ----------
        hef: (HEF) 
            HEF model object.

        Returns
        ----------
        list, list: 
            List of input stream layer information, List of output stream layer information.
        """
        input_vstream_info = hef.get_input_vstream_infos()
        output_vstream_info = hef.get_output_vstream_infos()

        for layer_info in input_vstream_info:
            logging_default.info('Input layer: {} {}'.format(layer_info.name, layer_info.shape))
        for layer_info in output_vstream_info:
            logging_default.info('Output layer: {} {}'.format(layer_info.name, layer_info.shape))
        
        return input_vstream_info, output_vstream_info
    
    def get_input_shape(self):
        """
        Get the shape of the model's input layer.

        Returns
        ----------
        tuple: 
            Shape of the model's input layer.
        """
        return self.hef.get_input_vstream_infos()[0].shape
    
    def get_output_shape(self):
        """
        Get the shape of the model's output layer.

        Returns
        ----------
        tuple: 
            Shape of the model's output layer.
        """
        return self.hef.get_output_vstream_infos()[0].shape
    
    def run(self, image : np.ndarray, output_vstream_info_indexes=[0]):
        """
        Run inference on Hailo-8 device.

        Parameters
        ----------
        image: numpy.ndarray) 
            Image to run inference on.

        Parameters
        ----------:
        list: 
            Inference output.
        """
        output_l = list(list())
        with InferVStreams(self.network_group, self.input_vstreams_params, self.output_vstreams_params) as infer_pipeline:            
            input_data = {self.input_vstream_info[0].name: image}   # Assumes that the model has one input

            with self.network_group.activate(self.network_group_params):
                output = infer_pipeline.infer(input_data)
                for output_vstream_info_index in output_vstream_info_indexes:
                    output_tmp = output[self.output_vstream_info[output_vstream_info_index].name]
                    output_l.append(output_tmp)

        return output_l
    
    def run_all(self, image : np.ndarray, hef_id : int) -> List[np.ndarray]:
        """
        Run inference on Hailo-8 device.

        Parameters
        ----------
        image: numpy.ndarray) 
            Image to run inference on.

        Returns:
            numpy.ndarray: Inference output.
        """
        network_group = self.network_group_list[hef_id]
        network_group_params = self.network_group_params_list[hef_id]
        input_vstreams_params = self.input_vstreams_params_list[hef_id]
        output_vstreams_params = self.output_vstreams_params_list[hef_id]
        input_vstream_info = self.input_vstream_info_list[hef_id]

        output = None
        with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as infer_pipeline:
            input_data = {input_vstream_info[0].name: image}   # Assumes that the model has one input

            with network_group.activate(network_group_params):
                output = infer_pipeline.infer(input_data)

        return output

    def release_device(self):
        """
        Release the Hailo device.
        """
        self.target.release()