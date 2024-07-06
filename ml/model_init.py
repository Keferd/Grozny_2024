from .configs.config import MainConfig
from confz import BaseConfig, FileSource
import os
from .utils.utils import load_detector, load_classificator, open_mapping, extract_crops
import time

main_config = MainConfig(config_sources=FileSource(file=os.path.join("ml", "configs", "config.yml")))
device = main_config.device
mapping = open_mapping(path_mapping=main_config.mapping)

detector_config = main_config.detector
classificator_config = main_config.classificator

# Load models
detector = load_detector(detector_config).to(device)
classificator = load_classificator(classificator_config).to(device)

# 0.9179973602294922