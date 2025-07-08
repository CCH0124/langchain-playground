## 普通 Dictionary（dict）VS 類型定義的 Dictionary（TypedDict）

1. Dictionary（dict）
```python
movie = {"name": "Avengers Endgame", "year": 2019}
```

優點：
- 快速、簡單：無需額外定義

- 彈性高：可以動態加入或刪除欄位

- 效能佳：查詢基於 key，很快

缺點：
- 不具型別檢查：key/value 沒有明確型別限制

- 不適用大型專案：難以維護、容易出錯

- 無法驗證結構：可能會出現錯誤格式但不報錯

2. TypedDict

```python
from typing import TypedDict

class Movie(TypedDict):
    name: str
    year: int

movie = Movie(name="Avengers Endgame", year=2019)

```

1. 優點：
-  Type Safety（型別安全）：明確定義 key 和型別，提升錯誤偵測能力

- 提升可讀性：一看就知道結構與內容是什麼

- 便於 IDE 補全與靜態分析：像是 Pyright、mypy 支援

2. 缺點：
- 較為冗長，需額外定義類別

- 運行時仍然是 dict，不會自動驗證（除非搭配工具）

## Union vs Optional

1. Union

```python
from typing import Union

def square(x: Union[int, float]) -> float:
    return x * x
```

`Union[int, float]` 表示 x 可以是 int 或 float 其中一種

函數接受 5 或 1.234 都合法

若傳入 `str`（如 "I am a string!"），靜態型別檢查工具（如 mypy）會報錯


- 靈活彈性：允許多種型別輸入

- 靜態型別檢查支援（Type Safety）：能及早發現錯誤

- 程式易懂：開發者一眼就知道哪些型別被允許

2. Optional

```python
from typing import Optional

def nice_message(name: Optional[str]) -> None:
    if name is None:
        print("Hey random person!")
    else:
        print(f"Hi there, {name}!")

```

`Optional[str]` 就是 `Union[str, None]` 的語法糖

表示 name 可以是 `str` 或 `None`

最常用於可選參數、缺省值、資料可能為空的情境

- 清晰表達「可為空」的情況
- 與 if is None 配合使用語意明確
- 對 IDE 與靜態檢查友善

## Any

```python
from typing import Any

def print_value(x: Any):
    print(x)

print_value("I pretend to be Batman in the shower sometimes")

```

- Any 表示：參數可以是任意型別
- Python 靜態型別檢查工具（如 mypy）會略過對此變數的型別檢查
- 可以傳入任何東西：int, str, list, None, 自訂類別都沒問題

- 極度彈性：允許一切可能的型別
- 適合暫時跳過型別檢查、快速原型設計
- 搭配泛型時可以用於開發通用函數（例如 JSON 處理）
##  Elements
### State 

State（狀態） 是一種共享的資料結構，用來儲存整個應用程式當前的資訊或上下文。簡單來說，它就像應用程式的記憶體，負責追蹤變數與資料，讓各個節點（nodes）在執行過程中可以讀取與修改這些資訊。像是

會議室裡的白板：
參與者（nodes）在白板（state）上寫入與讀取資訊，彼此保持同步，並協調要執行的動作。

### Nodes 
節點（Nodes） 是圖（graph）中執行特定任務的獨立函式或操作。每個節點會接收輸入（通常是目前的狀態），處理後產出輸出或更新後的狀態。像是

產線工作站（Assembly Line Stations）：
每一站執行一個工作，例如：裝配零件、上漆、品檢等等。

### Graph 在 LangGraph 中的意義
在 LangGraph 中，Graph（圖） 是一種總體結構，用來描繪各種任務（nodes）之間是如何連接與執行的。 它會視覺化整體工作流程，展示節點的執行順序，以及不同操作之間的條件分支與流程路徑。像是

路線圖（Road Map）：
像是一張連接城市的路線圖，城市之間的交叉口表示你可以根據情況選擇接下來要走哪條路（流程分支）。


### Edges 

Edges（邊） 是節點（nodes）之間的連線，用來決定流程的執行順序。它告訴系統在當前節點完成任務後，接下來要執行哪一個節點。像是

鐵道（Train Tracks）：
每一條軌道（edge）連接著兩個車站（nodes），指引列車（資料流程）下一站該去哪裡。

### Conditional Edges
條件邊（Conditional Edges）是一種特殊連線，根據當前狀態所符合的條件或邏輯，來決定接下來應該執行哪個節點。它們會根據某些邏輯判斷，將流程導向正確的下一步。像是

交通號誌（Traffic Lights）：
綠燈表示走這條路、紅燈表示停止、黃燈表示減速。燈的顏色（條件）決定接下來的行動方向。

### Start

START 節點 是 LangGraph 中的虛擬進入點，用來標示工作流程的開始位置。它本身不執行任何操作，只是作為整個圖的指定啟動點。像是:

比賽起跑線（Race Starting Line）：
就是比賽正式開始的地方，流程從這裡啟動。

### End
END 節點 表示 LangGraph 中流程的結束點。當流程抵達此節點時，圖的執行會終止，代表所有預期的處理步驟都已完成。像是

比賽終點線（Finish Line in a Race）：
一旦跨越此線，代表比賽結束了，任務完成。

### Tools

工具（Tools） 是特殊的函式或工具程式，節點（nodes）可用來執行特定任務，例如從 API 取得資料。它們為節點提供額外功能，增強其能力。節點屬於圖的架構部分，而工具則是在節點內部被呼叫使用的功能模組。像是

工具箱裡的工具（Tools in a Toolbox）：
如同使用鐵鎚釘釘子、螺絲起子轉螺絲，不同的工具有不同用途，根據任務選用適當的工具。

### ToolNode

ToolNode 是一種特殊的節點，主要用途是執行某個工具（Tool）。它會將工具的輸出結果寫回到共享狀態（State）中，讓其他節點可以使用這些資料。像是

操作者使用機器（Operator Using a Machine）：
操作者（ToolNode）操作機器（Tool），處理完後，將成果送回生產線供下一站使用。

### StateGraph 

StateGraph 是 LangGraph 中的類別，用來建立與編譯整個圖的結構。它負責管理所有的節點（nodes）、連線（edges）以及整體狀態（state），確保整個流程能統一運作，並讓資料能正確地在各元件之間流動。像是

建築藍圖（Blueprint of a Building）：
就像藍圖決定建築中各房間與連接關係，StateGraph 定義整個工作流程的結構與資料流向。

### Runnable 

在 LangGraph 中，Runnable 是一種標準化的、可執行元件，用來執行 AI 工作流程中的特定任務。它是建構模組化系統的基礎組件，讓我們能夠靈活組合各種工作流。像是


樂高積木（LEGO Brick）：
就像樂高積木可以組合起來形成複雜的結構，Runnable 也能組合在一起建立複雜的 AI 工作流程。


### Message 

| 類型                      | 說明翻譯                                             |
| ----------------------- | ------------------------------------------------ |
| 🧑 **Human Message**    | 使用者輸入的內容，例如「今天天氣如何？」                             |
| 💻 **System Message**   | 提供模型的設定或指令，例如「你是一位助理工程師」                         |
| 🤖 **AI Message**       | 模型產生的回覆，例如「今天天氣晴朗，最高溫 26 度」                      |
| 🧩 **Function Message** | 表示某個函式執行的結果（由 function call 回傳），如：「查詢結果是：26°C」   |
| 🔧 **Tool Message**     | 類似 Function Message，但專指由工具（如 ToolNode）所觸發的操作回傳結果 |

概念整理:

| 類型                | 誰送的？   | 內容是什麼？               | 何時出現？                 |
| ----------------- | ------ | -------------------- | --------------------- |
| `HumanMessage`    | 人類使用者  | 提問或指令                | 使用者啟動對話時              |
| `SystemMessage`   | 系統/開發者 | 設定模型角色或規則            | 對話一開始（初始化 prompt）     |
| `AIMessage`       | 模型     | LLM 回應的回答            | 每次模型輸出時               |
| `FunctionMessage` | 系統/模型  | 函式呼叫後的結果（如天氣 API 回傳） | 使用 function calling 時 |
| `ToolMessage`     | 工具執行者  | 工具執行後的結果（如計算器、DB 查詢） | 使用 LangGraph 工具流程時    |
