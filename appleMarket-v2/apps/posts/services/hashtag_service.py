import os

class HashtagService:
    def __init__(self):
        self.model = None
    
    def _load_model(self):
        if self.model is None:
            from ultralytics import YOLO
            self.model = YOLO('yolo11n.pt')
        return self.model
    
    def extract_hashtags(self, image_path):
        try:
            model = self._load_model()
            results = model(image_path)
            
            hashtags = set()
            for result in results:
                if result.boxes:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        class_name = result.names[class_id]
                        hashtags.add(class_name)
            
            return list(hashtags)
        
        except Exception as e:
            print(f"YOLO 에러: {e}")
            return []