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
        }
    }
}
```