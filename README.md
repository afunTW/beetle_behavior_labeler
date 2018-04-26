# beetle_behavior_labeler

## Input

- video_name.avi
- video_name.json

```
# video.json
{
    'res': {
        '1': {
            'path': [[]],   # 被標記的座標
            'n_frame': [],  # 被標記到 frame
            'wh': [[]]      # 被標記的寬高
        }, ...
    },
    'name': {
        '1': {
            'on': true or false,
            'ind': int,             # index
            'display_name': str     # 顯示名稱
        }, ...
    }
}
```

## Key binding

- ESC: 結束視窗
- LEFT / RIGHT: 向左/右 移動 10 個 frame, 並將移動後的位置設為 stop_frame
- Ctrl+LEFT / Ctrl+RIGHT:　向左/右 移動 1 個 frame, 並將移動後的位置設為 stop_frame
- RETURN: 回到 stop frame
- DOWN / UP: 向左/右 移動 10 個 frame
- SPACE: 新增行為紀錄
- Ctrl+a: 全選行為紀錄
- Key j: 跳到指定的 frame

