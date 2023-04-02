# Features
## Overview
The following table lists the supported places where executing can be used to map to a ast-node.
|          name          |         2.7        |         3.5        |         3.6        |         3.7        |         3.8        |         3.9        |        3.10        |        3.11        |       pypy2.7      |       pypy3.5      |       pypy3.6      |
|------------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
|    binary operators    | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|    `a(arguments...)`   | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|       compare ops      |(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|
|     `del obj.attr`     |(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |(:white_check_mark:)|(:white_check_mark:)|(:white_check_mark:)|
|    `del obj[index]`    |         :x:        |         :x:        |         :x:        |         :x:        | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |         :x:        |         :x:        |         :x:        |
|      format string     | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|       `obj.attr`       | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|      `obj[index]`      | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|inplace binary operators|         :x:        |         :x:        |         :x:        |         :x:        | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |         :x:        |         :x:        |         :x:        |
|      known issues      | :heavy_check_mark: |         :x:        |         :x:        |         :x:        |         :x:        |         :x:        |         :x:        | :heavy_check_mark: | :heavy_check_mark: |         :x:        |         :x:        |
|reverse binary operators| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|     `obj.attr = 5`     | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|   `obj[index]=value`   | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| `with contextmanager:` |         :x:        |         :x:        |         :x:        |         :x:        |(:white_check_mark:)|(:white_check_mark:)| :heavy_check_mark: | :heavy_check_mark: |         :x:        |         :x:        |         :x:        |
## Details

### binary operators

the node of an binary operation can be obtained inside a `__add__` or other binary operator.



|name|        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|----|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
| `+`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `-`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `/`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`//`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `*`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `%`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`**`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`<<`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`>>`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`\|`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `&`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `^`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `@`|                  |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|                  |:heavy_check_mark:|:heavy_check_mark:|

### `a(arguments...)`

the node of an binary operation can be obtained inside function or `__call__` operator.



| name |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|`call`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|

### compare ops

map compare ops:

* `t<5`: `__lt__` resolves to `ast.Compare(ops=[ast.Lt], ...)`
* `5<t`: `__gt__` resolves to `ast.Compare(ops=[ast.Gt], ...)`



|        name        |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|--------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|         `<`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|        `<=`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|         `>`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|        `>=`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|        `!=`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|        `==`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|        `in`        |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|      `not in`      |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `assert 5<t,"msg"` |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |
|    `assert 5<t`    |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |
|      `if 5<t:`     |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|       `5<t<6`      |        :x:       |        :x:       |        :x:       |        :x:       |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|        :x:       |        :x:       |        :x:       |
|   `assert 5<t<6`   |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |:heavy_check_mark:|        :x:       |        :x:       |        :x:       |
|     `if 5<t<6:`    |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |:heavy_check_mark:|:heavy_check_mark:|        :x:       |        :x:       |        :x:       |
|`if 5<t<6 or 8<t<9:`|        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |        :x:       |:heavy_check_mark:|        :x:       |        :x:       |        :x:       |        :x:       |

### `del obj.attr`

the node can be accessed inside the `__delattr__` function.



|         name        |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|---------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|    `del obj.attr`   |        :x:       |        :x:       |        :x:       |        :x:       |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|        :x:       |        :x:       |        :x:       |
|`delattr(obj,"attr")`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|

### `del obj[index]`

the node can be accessed inside the `__delitem__` function.



|        name        |2.7|3.5|3.6|3.7|        3.8       |        3.9       |       3.10       |       3.11       |pypy2.7|pypy3.5|pypy3.6|
|--------------------|---|---|---|---|------------------|------------------|------------------|------------------|-------|-------|-------|
|  `del obj[index]`  |:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
|`del obj[start:end]`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |

### format string

expressions inside format strings



|      name     |2.7|3.5|        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |pypy2.7|pypy3.5|      pypy3.6     |
|---------------|---|---|------------------|------------------|------------------|------------------|------------------|------------------|-------|-------|------------------|
|`format string`|   |   |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|       |       |:heavy_check_mark:|

### `obj.attr`

the node can be accessed inside the `__getattr__` function.



|         name        |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|---------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|      `obj.attr`     |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`getattr(obj,"attr")`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|

### `obj[index]`

the node can be accessed inside the `__getitem__` function.



|      name      |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|----------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|  `obj[index]`  |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`obj[start:end]`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|

### inplace binary operators

the node of an binary operation can be obtained inside a `__iadd__` or other binary operator.



| name|2.7|3.5|3.6|3.7|        3.8       |        3.9       |       3.10       |       3.11       |pypy2.7|pypy3.5|pypy3.6|
|-----|---|---|---|---|------------------|------------------|------------------|------------------|-------|-------|-------|
| `+=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `-=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `/=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
|`//=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `*=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `%=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
|`**=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
|`<<=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
|`>>=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
|`\|=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `&=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `^=`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `@=`|   |:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|       |  :x:  |  :x:  |

### known issues

some known issues



|      name      |        2.7       |3.5|3.6|3.7|3.8|3.9|3.10|       3.11       |      pypy2.7     |pypy3.5|pypy3.6|
|----------------|------------------|---|---|---|---|---|----|------------------|------------------|-------|-------|
|`same generator`|:heavy_check_mark:|:x:|:x:|:x:|:x:|:x:| :x:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |

### reverse binary operators

the node of an binary operation can be obtained inside a `__radd__` or other binary operator.



|name|        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|----|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
| `+`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `-`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `/`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`//`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `*`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `%`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`**`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`<<`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`>>`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`\|`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `&`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `^`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `@`|                  |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|                  |:heavy_check_mark:|:heavy_check_mark:|

### `obj.attr = 5`

the node can be accessed inside the `__setattr__` function.



|         name         |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|----------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|     `t.attr = 5`     |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`t.attr, g.attr= 5, 5`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
| `setattr(t,"attr",5)`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|

### `obj[index]=value`

the node can be accessed inside the `__setitem__` function.



|         name         |        2.7       |        3.5       |        3.6       |        3.7       |        3.8       |        3.9       |       3.10       |       3.11       |      pypy2.7     |      pypy3.5     |      pypy3.6     |
|----------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
|  `obj[index]=value`  |:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|`obj[start:end]=value`|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|

### `with contextmanager:`

__enter__ and __exit__



|    name   |2.7|3.5|3.6|3.7|        3.8       |        3.9       |       3.10       |       3.11       |pypy2.7|pypy3.5|pypy3.6|
|-----------|---|---|---|---|------------------|------------------|------------------|------------------|-------|-------|-------|
|`__enter__`|:x:|:x:|:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |
| `__exit__`|:x:|:x:|:x:|:x:|        :x:       |        :x:       |:heavy_check_mark:|:heavy_check_mark:|  :x:  |  :x:  |  :x:  |