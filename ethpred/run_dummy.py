import numpy as np
import torch
from .pipeline.generate_data import generate_data, create_dataloaders
from .models.configure_model import configure_model
from .training.training_loops import GRU_training
from .training.logger import Logger


def run_dummy(cnf: dict):
    np.random.seed(42)
    torch.manual_seed(42)

    X_train, X_test, y_train, y_test = generate_data(cnf)


    # print(X_train[0])
    # print(y_train[0])

    train, test = create_dataloaders(X_train, y_train, X_test, y_test, cnf)
    model = configure_model(cnf)

    logger = Logger(cnf)

    GRU_training(model=model,
                 train_dataloader=train,
                 test_dataloader=test,
                 cnf=cnf['training'],
                 logger=logger)
