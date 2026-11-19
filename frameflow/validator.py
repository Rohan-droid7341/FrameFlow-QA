from typing import List, Dict, Any, Tuple

class TemporalValidator:
    """Validates temporal boundaries, jitter, and segment consistency in video annotations."""

    def __init__(self, fps: float = 30.0, min_duration_sec: float = 0.5):
        self.fps = fps
        self.min_duration_sec = min_duration_sec

    def validate_batch(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs comprehensive validation checks across chronological video segments."""
        sorted_segs = sorted(segments, key=lambda s: s.get("start_time", 0.0))
        
        overlaps = []
        gaps = []
        short_segments = []
        total_duration = 0.0

        for i, seg in enumerate(sorted_segs):
            start = float(seg.get("start_time", 0.0))
            end = float(seg.get("end_time", 0.0))
            duration = max(0.0, end - start)
            total_duration += duration

            # Check 1: Inverted timestamps
            if end <= start:
                overlaps.append({
                    "segment_id": seg.get("segment_id", f"seg_{i}"),
                    "error_type": "inverted_boundary",
                    "details": f"End time ({end}s) <= Start time ({start}s)"
                })

            # Check 2: Micro-jitter / sub-threshold intervals
            if 0 < duration < self.min_duration_sec:
                short_segments.append({
                    "segment_id": seg.get("segment_id", f"seg_{i}"),
                    "duration": duration,
                    "action": seg.get("action", "unknown")
                })

            # Check 3: Inter-segment overlap or gap
            if i > 0:
                prev_seg = sorted_segs[i - 1]
                prev_end = float(prev_seg.get("end_time", 0.0))
                
                # Overlap detection (collision)
                if start < prev_end - (1.0 / self.fps):
                    overlap_dur = round(prev_end - start, 3)
                    overlaps.append({
                        "prev_segment": prev_seg.get("segment_id", f"seg_{i-1}"),
                        "curr_segment": seg.get("segment_id", f"seg_{i}"),
                        "overlap_seconds": overlap_dur,
                        "error_type": "temporal_collision"
                    })
                # Gap detection (unlabeled interval)
                elif start > prev_end + (1.0 / self.fps):
                    gap_dur = round(start - prev_end, 3)
                    gaps.append({
                        "prev_segment": prev_seg.get("segment_id", f"seg_{i-1}"),
                        "curr_segment": seg.get("segment_id", f"seg_{i}"),
                        "gap_seconds": gap_dur
                    })

        defect_count = len(overlaps) + len(gaps) + len(short_segments)
        precision_rate = max(0.0, 100.0 - (defect_count / max(1, len(sorted_segs)) * 100.0 * 0.1))

        return {
            "total_segments": len(sorted_segs),
            "total_annotated_duration_sec": round(total_duration, 2),
            "defect_count": defect_count,
            "compliance_precision_pct": round(precision_rate, 2),
            "overlaps": overlaps,
            "gaps": gaps,
            "short_segments": short_segments
        }
