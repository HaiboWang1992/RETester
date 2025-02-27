## Chi-squared test of independence result for each category pair

| **Category Pair**                                 | **𝜒2**   | **p-value** | **Description** |
| :-----------------------------------------------: | :-------: | :---------: | :-------------: |
| (Root Cause, Symptom)                             | 328\.638  | 1\.884e-34  | Related         |
| (Refactoring Type, Root Cause)                    | 714\.225  | 0\.003      | Related         |
| (Refactoring Type, Symptom)                       | 1405\.076 | 1\.000      | Not related     |
| (Input program characteristic, Refactoring Type)  | 4374\.049 | 1\.941e-6   | Related         |
| (Input program characteristic, Root Cause)        | 377\.659  | 1\.198e-4   | Related         |
| (Input program characteristic, Symptom)           | 935\.347  | 1\.867e-22  | Related         |


## Post hoc analysis result for variables in each category pair

### Post hoc analysis result for variables in (Root Cause, Symptom)

| **Variable pair**                                     | **Adjusted p-value** |
| :---------------------------------------------------: | :------------------: |
| (failed selection parsing, refactoring not available) | 1\.374e-34           |
| (incorrect transformations, comment related)          | 0\.008               |
| (others, bad performance)                             | 2\.334e-17           |
| (incorrect type resolving, failed refactoring)        | 0\.019               |

### Post hoc analysis result for variables in (Refactoring Type, Root Cause)

| **Variable pair**                                                      | **Adjusted p-value** |
| :--------------------------------------------------------------------: | :------------------: |
| (Use supertype wherever possible, Incorrect Type Resolving)            | 4\.718e-4            |
| (rename variable, failed selection parsing)                            | 4\.723e-6            |
| (rename enum, failed selection parsing)                                | 2\.006e-6            |
| (convert local variable , Incorrect Type Resolving)                    | 0\.008               |
| (extract method, incorrect flow analysis)                              | 0\.002               |
| (inline constant, Incorrect Type Resolving)                            | 0\.008               |
| (extract constant, failed selection parsing)                           | 0\.003               |
| (Convert String concatenation to Text Block, incorrect type resolving) | 0\.041               |
| (rename interface, incorrect type resolving)                           | 0\.041               |
| (replace anonymous with lambda, incorrect type resolving)              | 0\.041               |
| (convert to instance method, incorrect type resolving)                 | 0\.041               |

### Post hoc analysis result for variables in (Input program characteristic, Refactoring Type)

| **Variable pair**                                        | **Adjusted p-value** |
| :------------------------------------------------------: | :------------------: |
| (super constructor, extract superclass)                  | 7\.610e-26           |
| (overloaded method, generalize type)                     | 4\.062e-7            |
| (overloaded method, Move Static Members)                 | 0\.032               |
| (overloaded method, delete method)                       | 4\.062e-7            |
| (instanceof, change class signature)                     | 0\.003               |
| (switch case, convert local variable)                    | 9\.338e-6            |
| (record, Move member type to new File)                   | 1\.458e-5            |
| (record, introduce factory)                              | 0\.011               |
| (varargs, introduce parameter)                           | 0\.001               |
| (joint variable declaration, inline local variable)      | 4\.817e-7            |
| (static initializer, inline field)                       | 1\.199e-4            |
| (static initializer, move field)                         | 1\.199e-4            |
| (var type, rename variable)                              | 7\.837e-4            |
| (var type, move class)                                   | 7\.837e-4            |
| (var type, convert local variable)                       | 1\.443e-16           |
| (inner class, Move Member Type to New File)              | 7\.741e-9            |
| (comment related, change method signature)               | 2\.476e-4            |
| (anonymous class, convert anonymous to nested class)     | 2\.541e-7            |
| (anonymous class, Change method Signature)               | 0\.003               |
| (anonymous class, Convert Anonymous to nested class)     | 0\.003               |
| (anonymous class, convert anonymous to inner class)      | 0\.003               |
| (anonymous class, parameterize anonymous to inner class) | 0\.003               |
| (foreach, replace foreach with for)                      | 5\.124e-9            |
| (foreach, invert boolean)                                | 0\.003               |
| (synchronized block, Move member Type to new File)       | 5\.213e-54           |
| (arithmetic expression, inline expression)               | 5\.897e-26           |
| (nested constructor, introduce factory)                  | 1\.443e-16           |
| (static import, encapsulate field)                       | 8\.450e-12           |
| (vector, Infer Type Arguments)                           | 3\.409e-20           |
| (bounded type, Introduce Factory)                        | 5\.213e-54           |
| (local class, push down method)                          | 0\.033               |
| (local class, rename class)                              | 0\.033               |
| (local class, introduce field)                           | 1\.199e-4            |
| (try catch, Surround With Try/Catch)                     | 1\.443e-16           |
| (multi dimension array, extract constant)                | 1\.199e-4            |
| (instance of, Extract Variable)                          | 5\.213e-54           |
| (implicit class, Introduce constant)                     | 5\.897e-26           |
| (implicit class, introduce variable)                     | 4\.817e-7            |
| (special string, introduce constant)                     | 7\.439e-12           |
| (nested calls, extract parameter)                        | 1\.443e-16           |
| (try-with-resources, introduce field)                    | 1\.199e-4            |
| (try-with-resources, delete variable)                    | 7\.439e-12           |
| (try-with-resources, unwarp try)                         | 7\.439e-12           |
| (cyclically dependent class, pull members up)            | 5\.897e-26           |
| (recursive method, invert boolean)                       | 5\.897e-26           |
| (functional interface, change method interface)          | 5\.897e-26           |

### Post hoc analysis result for variables in (Input program characteristic, Root Cause)

| **Variable pair**                          | **Adjusted p-value** |
| :----------------------------------------: | :------------------: |
| (record, incorrect preconditions checking) | 0\.035               |
| (toString(), others)                       | 8\.246e-20           |
| (var type, Incorrect Type Resolving)       | 1\.794e-3            |
| (special string, failed selection parsing) | 1\.361e-3            |
| (nested calls, incorrect type resolving)   | 7\.060e-3            |
| (foreach, incorrect type resolving)        | 7\.060e-3            |
| (static method, incorrect type resolving)  | 7\.060e-3            |

### Post hoc analysis result for variables in (Input program characteristic, Symptom)

| **Variable pair**                              | **Adjusted p-value** |
| :--------------------------------------------: | :------------------: |
| (toString(), bad performance)                  | 7\.820e-55           |
| (var type, others)                             | 2\.164e-17           |
| (comment related, comment related)             | 1\.921e-42           |
| (arithmetic expression, behavior change)       | 0\.044               |
| (local class, compiler error)                  | 1\.116e-12           |
| (nested calls, failed refactoring)             | 0\.009               |
| (java ternary conditional, unnecessary change) | 1\.401e-6            |
| (type cast, unnecessary change)                | 1\.401e-6            |
