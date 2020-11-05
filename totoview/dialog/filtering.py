
from ..core.basewindow import BaseWindow
import toto
import matplotlib.pyplot as plt


class FiltWindow(BaseWindow):
    def __init__(self,X,LonLat=[None],parent=None):
        super(FiltWindow, self).__init__(folder=toto.filters,title='Filtering toolbox',parent=parent)
        self.X0=X[0].copy()
        self.X=X
        self.LonLat=LonLat
        self.refresh_plot()

    # def refresh_plot(self):
    #     self.figure.clf()
    #     ax = self.figure.add_subplot(111)

    #     ax.plot(self.X0[self.X[0].keys()[0]],label='original')
    #     ax.plot(self.X[0][self.X[0].keys()[0]],label='filter')
    #     plt.grid()
    #     self.figure.autofmt_xdate()
    #     ax.legend()
    #     self.canvas.draw()


    def filter(self):
        idx=self.method_names.currentItem()
        fct_name=idx.text()
        run_ft=self._import_from('toto.filters.%s' % fct_name,fct_name)
        opt=self.get_options(self.opt[self.method_names.currentRow()]) # get all option as dict
        opt['LonLat']=self.LonLat[0]
        #Only play with first file and first variable
        self.X[0][self.X[0].keys()[0]]=run_ft(self.X[0][self.X[0].keys()[0]],opt)

        self.refresh_plot()

    def save(self):
        idx=self.method_names.currentItem()
        fct_name=idx.text()
        run_ft=self._import_from('toto.filters.%s' % fct_name,fct_name)
        opt=self.get_options(self.opt[self.method_names.currentRow()]) # get all option as dict

        for i in range(0,len(self.X)):
            opt['LonLat']=self.LonLat[i]
            for var in self.X[i].keys():
                self.X[i][var]=run_ft(self.X[i][var],opt)

        self.close()
    def reset(self):
        self.X[0][self.X[0].keys()[0]]=self.X0[self.X[0].keys()[0]]
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