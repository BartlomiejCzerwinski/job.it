import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

class JobMatchingVectorizer:
    def __init__(self, n_neighbors: int = 5):
        # Maximum skill level (assuming levels are 1-3)
        self.max_level = 3
        # Initialize KNN model with cosine similarity
        self.knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')

    def _normalize_level(self, level: int) -> float:
        """Normalize skill level to range [0, 1]."""
        return level / self.max_level

    def create_skill_vector(self, skills: List[Dict[str, Any]]) -> List[Tuple[int, float]]:
        """
        Create a vector of skills in format [(skillId, normalized_level), (skillId, normalized_level), ...]
        where normalized_level is in range [0, 1]
        """
        return [(skill['id'], self._normalize_level(skill['level'])) for skill in skills]

    def _vector_to_array(self, vector: List[Tuple[int, float]], max_skill_id: int) -> np.ndarray:
        """
        Convert skill vector to numpy array where index is skill_id and value is normalized level.
        """
        array = np.zeros(max_skill_id + 1)
        for skill_id, level in vector:
            array[skill_id] = level
        return array

    def find_matches(self, user_vector: List[Tuple[int, float]], job_vectors: List[Dict]) -> List[Dict]:
        """
        Find best matching jobs using KNN with cosine similarity.
        Returns list of jobs with their match scores, ordered from best to worst match.
        If no matches are found, returns all jobs with 0 match score.
        """
        # If no jobs, return empty list
        if not job_vectors:
            return []

        # If no user skills, return all jobs with 0 match score
        if not user_vector:
            return [{
                'listing_id': job['listing_id'],
                'title': job['title'],
                'match_score': 0.0
            } for job in job_vectors]

        # Find maximum skill ID to determine vector size
        max_skill_id = max(
            max(skill_id for skill_id, _ in user_vector),
            max(skill_id for job in job_vectors for skill_id, _ in job['vector'])
        )

        # Convert user vector to array
        user_array = self._vector_to_array(user_vector, max_skill_id).reshape(1, -1)

        # Convert job vectors to array
        job_arrays = np.array([
            self._vector_to_array(job['vector'], max_skill_id)
            for job in job_vectors
        ])

        # Calculate cosine similarity between user and all jobs
        similarities = cosine_similarity(user_array, job_arrays)[0]

        # Create matches with similarity scores
        matches = []
        for idx, similarity in enumerate(similarities):
            job = job_vectors[idx]
            # Only consider positive similarities and scale to 0-100%
            match_score = round(float(max(0, similarity) * 100), 2)
            matches.append({
                'listing_id': job['listing_id'],
                'title': job['title'],
                'match_score': match_score
            })

        # Sort matches by score (highest first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches
