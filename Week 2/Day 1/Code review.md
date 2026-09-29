| **Where** | Src main.py line 1   |
| --------- | -------------------- |
| **What**  | Imports disorganized |
| **Class** | Machine : ruff       |
| **Ask**   | Organize imports     |

| **Where** | Src main.py lines 1                  |
| --------- | ------------------------------------ |
| **What**  | Import unused                        |
| **Class** | Machine : ruff                       |
| **Ask**   | Remove unused import (fastapi.Query) |

| **Where** | Src main.py line 3           |
| --------- | ---------------------------- |
| **What**  | 'typing .List' is deprecated |
| **Class** | Machine : ruff               |
| **Ask**   | Use 'list' instead           |

| **Where** | Src main.py line 3                   |
| --------- | ------------------------------------ |
| **What**  | 'typing.List' is imported and unused |
| **Class** | Machine : ruff                       |
| **Ask**   | Remove unused import                 |

| **Where** | Src main.py line 24                    |
| --------- | -------------------------------------- |
| **What**  | Use \`X \| None\` for type annotations |
| **Class** | Machine : ruff                         |
| **Ask**   | Convert to \`X \| None                 |

| **Where** | Src main.py lines 1 - 3                   |
| --------- | ----------------------------------------- |
| **What**  | Import block is un-sorted or un-formatted |
| **Class** | Machine : ruff                            |
| **Ask**   | organize imports                          |

| **Where** | Src main.py line 31                    |
| --------- | -------------------------------------- |
| **What**  | Use \`X \| None\` for type annotations |
| **Class** | Machine : ruff                         |
| **Ask**   | Convert to \`X \| None                 |

| **Where** | Project folder                                                                                            |
| --------- | --------------------------------------------------------------------------------------------------------- |
| **What**  | source file found twice under different module names : main & src.main                                    |
| **Class** | Machine : mypy                                                                                            |
| **Ask**   | adding \`\__init_\_.py\` in the src file, or using \`--explicit-package-bases\` or adjusting \`MYPYPATH\` |

**Verdict: Disapprove  
Too many machine errors (ruff and mypy)**