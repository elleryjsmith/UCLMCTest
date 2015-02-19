# Results
Results can be run by

```
$ python main.py
```

### 31 Jan 2015

| Description | mc160.dev | mc500.dev | mc160.train | mc500.train | ['mc160.dev', 'mc160.train'] | ['mc500.dev', 'mc500.train'] |
| --- | ------ | ------ | ------ | ------ | ------ | --- |
| Baseline (BOW) | 0.563194444444 | 0.485416666667 | 0.566369047619 | 0.522777777778 | 0.565416666667 | 0.51744047619 |
| Baseline (BOW) all | 0.502083333333 | 0.425833333333 | 0.555357142857 | 0.411388888889 | 0.539375 | 0.413452380952 |
| Baseline (BOW) w/ stopwords | 0.509722222222 | 0.4775 | 0.563988095238 | 0.531666666667 | 0.547708333333 | 0.523928571429 |
| SVM (BOW) train mc160train | 0.563194444444 | 0 | 0 | 0 | 0 | 0 |
| SVM (BOW) train mc500train | 0 | 0.485416666667 | 0 | 0 | 0 | 0 |
| LogReg (BOW+BOWall) mc160train | 0.577083333333 | 0 | 0 | 0 | 0 | 0 |
| LogReg (BOW+BOWall) mc500train | 0 | 0.507916666667 | 0 | 0 | 0 | 0 |