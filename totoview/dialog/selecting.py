from ..core.basewindow import BaseWindow
import toto
import matplotlib.pyplot as plt
import pandas as pd

class SelectWindow(BaseWindow):
    def __init__(self,X, parent=None):
        super(SelectWindow, self).__init__(folder=toto.selections,title='Selection toolbox',parent=parent)

        self.X0=X[0].copy()
        self.X=X
        self.refresh_plot()

    # def refresh_plot(self):
    #     self.figure.clf()
    #     ax = self.figure.add_subplot(111)

    #     ax.plot(self.X0[self.X0.keys()[0]],label='original')
    #     ax.plot(self.X[0][self.X[0].keys()[0]],label='selected')
    #     plt.grid()
    #     self.figure.autofmt_xdate()
    #     ax.legend()
    #     self.canvas.draw()


    def filter(self):
        idx=self.method_names.currentItem()
        fct_name=idx.text()
        run_ft=self._import_from('toto.selections.%s' % fct_name,fct_name)
        opt=self.get_options(self.opt[self.method_names.currentRow()]) # get all option as dict
        #Only play with first file and first variable
        new_df=run_ft(self.X[0][self.X[0].keys()[0]],opt)
        if isinstance(new_df, pd.DataFrame):
            self.X[0]=new_df
        else:
            self.X[0][self.X[0].keys()[0]]=new_df

        self.refresh_plot()

    def save(self):
        self.reset()
        idx=self.method_names.currentItem()
        fct_name=idx.text()
        run_ft=self._import_from('toto.selections.%s' % fct_name,fct_name)
        opt=self.get_options(self.opt[self.method_names.currentRow()]) # get all option as dict
        for i in range(0,len(self.X)):
            for var in self.X[i].keys():
                new_df=run_ft(self.X[i][var],opt)
                if isinstance(new_df, pd.DataFrame):
                    for new_var in new_df.keys():
                        self.X[i][new_var]=new_df[new_var]
                    del self.X[i][var]
                else:
                    self.X[i][var]=new_df

        self.close()
    def reset(self):
        self.X[0]=self.X0.copy()
        self.refresh_plot()

    def cancel(self):
        self.X[0]=self.X0
        self.close()
        return None
    
    def exec(self):
        self.exec_()
        return self.X


if __name__ == '__main__':
    app = QApplication(sys.argv)
    import numpy as np
    import pandas as pd
    dates = pd.date_range('1/1/2000', periods=8)
    df = pd.DataFrame(np.random.randn(8, 4),index=dates, columns=['A', 'B', 'C', 'D'])

    main = FiltWindow([df])
    main.setWindowTitle('Filtering toolbox')
    main.show()

    sys.exit(app.exec_())