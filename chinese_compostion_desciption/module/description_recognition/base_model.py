import os
from metric_utils import *



def init_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

class BaseModel():
    def __init__(self, config):
        self.config = config
        self.batch_size = int(self.config.get('batch_size', 32))
        self.max_len = int(self.config.get('max_len', 128))
        self.epochs = int(self.config.get("epochs", 100))
        self.patience = int(self.config.get("patience", 5))
        self.save_dir = self.config['save_dir']
        self.seed = int(self.config.get('seed',-1))
        self.num_labels = 2
        # self.n_gpu = int(self.config.get('n_gpu',1))
        init_dir(self.save_dir)

    def train(self, train_path, dev_path, test_path):
        """train model use train_path
        Parameters
        ----------
            model_path: model_path
        Returns
        -------
            report:model performance in test
        """
        raise NotImplementedError

    def load_model(self, model_path):
        """load model from model_path
        Parameters
        ----------
            model_path: model_path
        Returns
        -------
            None
        """
        raise NotImplementedError
    
    def demo(self,text):
        """demo for one text
        Parameters
        ----------
            text: input text
        Returns
        -------
            p:the probability of text
        """
        raise NotImplementedError

    def demo_text_list(self,text_list):
        """demo input text_list 
        Parameters
        ----------
            text_list: text_list
        Returns
        -------
            p_list:the probability of all text
        """
        raise NotImplementedError

    def predict(self,text):
        return self.demo(text)
    
    def predict_list(self,text_list):
        return self.demo_text_list(text_list)

    def evaluate(self,df):
#         df = load_df(df)
        y_pred = self.demo_text_list(df['text'].tolist())
        y_pred = np.array(y_pred)
        y_true = df['label']
        if self.num_labels==2:
            report = get_model_metrics(y_true,y_pred)
        else:
            report = get_multi_class_report(y_true,y_pred)
        return report

    def release(self):
        pass