/**
 * Tests for the quiz page (/quiz/[sessionId]).
 * MSW intercepts fetch calls; next/navigation is mocked.
 */
import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

// ---------------------------------------------------------------------------
// Mock next/navigation
// ---------------------------------------------------------------------------
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useParams: () => ({ sessionId: "test-session-123" }),
  useRouter: () => ({ push: mockPush }),
}));

// Mock next/image — renders a plain <img>
vi.mock("next/image", () => ({
  default: (props: React.ImgHTMLAttributes<HTMLImageElement> & { alt: string }) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} />;
  },
}));

// ---------------------------------------------------------------------------
// Fixture data
// ---------------------------------------------------------------------------
const SESSION_ID = "test-session-123";

const FIXTURE_SESSION = {
  session_id: SESSION_ID,
  exam_id: "74",
  questions: [
    {
      question_no: 1,
      exam_id: "74",
      image_path: "data/processed/history_exam/74/problem_image/74_workbook_page_1_q1.png",
      points: 2,
    },
    {
      question_no: 2,
      exam_id: "74",
      image_path: "data/processed/history_exam/74/problem_image/74_workbook_page_1_q2.png",
      points: 2,
    },
    {
      question_no: 3,
      exam_id: "74",
      image_path: "data/processed/history_exam/74/problem_image/74_workbook_page_1_q3.png",
      points: 3,
    },
  ],
  answers: {},
  submitted: false,
  total_questions: 3,
};

const SESSION_AFTER_ANSWER = {
  ...FIXTURE_SESSION,
  answers: { "74_1": 3 },
};

const SUBMIT_RESULT = {
  session_id: SESSION_ID,
  score: 2,
  total: 3,
  points_earned: 4,
  total_points: 7,
  results: [
    {
      question_no: 1,
      exam_id: "74",
      image_path: "data/processed/history_exam/74/problem_image/74_workbook_page_1_q1.png",
      selected_answer: 3,
      correct_answer: 2,
      is_correct: false,
      points: 2,
      points_earned: 0,
    },
    {
      question_no: 2,
      exam_id: "74",
      image_path: "data/processed/history_exam/74/problem_image/74_workbook_page_1_q2.png",
      selected_answer: 1,
      correct_answer: 1,
      is_correct: true,
      points: 2,
      points_earned: 2,
    },
    {
      question_no: 3,
      exam_id: "74",
      image_path: "data/processed/history_exam/74/problem_image/74_workbook_page_1_q3.png",
      selected_answer: 5,
      correct_answer: 5,
      is_correct: true,
      points: 3,
      points_earned: 3,
    },
  ],
};

// ---------------------------------------------------------------------------
// MSW server
// ---------------------------------------------------------------------------
let answerCallCount = 0;

const server = setupServer(
  http.get(`/api/quiz/${SESSION_ID}`, () => HttpResponse.json(FIXTURE_SESSION)),
  http.post(`/api/quiz/${SESSION_ID}/answer`, () => {
    answerCallCount++;
    return HttpResponse.json(SESSION_AFTER_ANSWER);
  }),
  http.post(`/api/quiz/${SESSION_ID}/submit`, () => HttpResponse.json(SUBMIT_RESULT)),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  answerCallCount = 0;
  mockPush.mockClear();
});
afterAll(() => server.close());

// ---------------------------------------------------------------------------
// Import the page AFTER mocks are set up
// ---------------------------------------------------------------------------
import QuizPage from "@/app/quiz/[sessionId]/page";

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("QuizPage", () => {
  it("renders the first question with progress bar", async () => {
    render(<QuizPage />);

    await waitFor(() => {
      expect(screen.getByText(/Question 1 of 3/i)).toBeInTheDocument();
    });

    // Progress bar element exists
    const bar = document.querySelector(".bg-blue-500");
    expect(bar).toBeInTheDocument();
  });

  it("highlights the selected answer and enables Next navigation", async () => {
    render(<QuizPage />);
    await waitFor(() => screen.getByText(/Question 1 of 3/i));

    // Click answer button ③ (index 2 → value 3)
    const buttons = screen.getAllByRole("button");
    const answerButtons = buttons.filter((b) =>
      ["①", "②", "③", "④", "⑤"].includes(b.textContent ?? "")
    );
    expect(answerButtons).toHaveLength(5);

    fireEvent.click(answerButtons[2]); // ③

    await waitFor(() => {
      // After click the session is updated with the answer; button should be highlighted
      expect(answerButtons[2]).toHaveClass("bg-blue-600");
    });
  });

  it("shows Submit button on the last question", async () => {
    render(<QuizPage />);
    await waitFor(() => screen.getByText(/Question 1 of 3/i));

    // Navigate to last question (click Next twice)
    const nextBtn = screen.getByRole("button", { name: /next/i });
    fireEvent.click(nextBtn);
    await waitFor(() => screen.getByText(/Question 2 of 3/i));

    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await waitFor(() => screen.getByText(/Question 3 of 3/i));

    expect(screen.getByRole("button", { name: /submit quiz/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /next/i })).not.toBeInTheDocument();
  });

  it("navigates to result page after submission", async () => {
    render(<QuizPage />);
    await waitFor(() => screen.getByText(/Question 1 of 3/i));

    // Go to last question
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await waitFor(() => screen.getByText(/Question 2 of 3/i));
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await waitFor(() => screen.getByText(/Question 3 of 3/i));

    // Submit
    fireEvent.click(screen.getByRole("button", { name: /submit quiz/i }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(`/quiz/${SESSION_ID}/result`);
    });
  });
});
