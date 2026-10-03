class InjurySeverityEngine:
    """Calculates apparent injury severity (Minor vs Moderate vs Critical)."""

    @staticmethod
    def calculate_severity(yolo_result):
        injuries = yolo_result.get('injuries', [])
        wound_area = yolo_result.get('wound_area_pixels', 0)
        
        critical_indicators = [
            'severe visible trauma', 'possible fracture or abnormal limb position',
            'deep open wound', 'heavy visible bleeding'
        ]

        # Check for critical keywords
        for inj in injuries:
            if any(crit in inj.lower() for crit in critical_indicators):
                return 'CRITICAL', 'Critical condition detected. Animal requires immediate veterinary ambulance dispatch and surgical stabilization.'

        if wound_area > 2500 or len(injuries) >= 2:
            return 'CRITICAL', 'Substantial trauma and open bleeding detected. High priority emergency.'
        elif wound_area > 600 or len(injuries) == 1:
            return 'MODERATE', 'Moderate visible injury detected. Requires prompt cleaning, dressing, and clinical observation.'
        else:
            return 'NORMAL', 'Minor visible abrasions or non-critical condition. General first aid and shelter monitoring recommended.'