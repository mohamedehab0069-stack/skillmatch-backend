from backend.models.task import TaskSubmission, PortfolioItem
from backend.models.student import StudentProfile
from backend.models.notification import Notification
from backend.models.user import User


def auto_generate_portfolio(submission_id: int, student_profile: dict) -> int:
    """
    Called after a task submission is approved.
    Creates a portfolio item and verifies any skills gained.
    Returns the new portfolio_item_id.
    """
    submission = TaskSubmission.get_by_id(submission_id)
    if not submission:
        raise ValueError(f"Submission {submission_id} not found.")

    title       = f"Completed: {submission.get('task_title', 'Task')}"
    description = (
        f"Successfully completed a {submission.get('difficulty','medium')}-difficulty task "
        f"and scored {submission.get('score', 0)} points."
    )
    item_url    = submission.get("submission_url", "")

    portfolio_id = PortfolioItem.create(
        student_id    = student_profile["id"],
        submission_id = submission_id,
        title         = title,
        description   = description,
        item_url      = item_url,
    )

    # Notify student
    student_user = User.find_by_id(student_profile["user_id"])
    if student_user:
        Notification.create(
            user_id = student_user["id"],
            title   = "Task approved — portfolio updated!",
            message = f"Your submission for '{submission.get('task_title','the task')}' was approved "
                      f"and added to your portfolio. Score: {submission.get('score',0)} points.",
            ntype   = "success"
        )

    return portfolio_id
