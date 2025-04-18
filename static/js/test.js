
console.log("Test JS loaded");
        // Theme Toggle Functionality
        const themeToggle = document.getElementById('themeToggle');
        let currentTheme = localStorage.getItem('theme') || 'light';
        
        // Apply saved theme or default to light
        function applyTheme() {
            document.documentElement.setAttribute('data-theme', currentTheme);
            themeToggle.textContent = currentTheme === 'dark' ? '☀️' : '🌑';
            localStorage.setItem('theme', currentTheme);
        }
        
        // Initialize theme
        applyTheme();
        
        // Toggle theme on button click
        themeToggle.addEventListener('click', () => {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme();
        });

        // Test Functionality
        let currentQuestion = 1;
        const totalQuestions = parseInt("{{ paper.no_of_qs }}", 10) || 0;
        const questionCards = document.querySelectorAll('.question-card');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const questionBoxesContainer = document.getElementById('question-boxes-container');
        const answeredQuestions = new Set();
        const doubtQuestions = new Set();
        let timerInterval, malpracticeInterval;
        let formSubmitted = false;

        // Initialize question boxes
        function initializeQuestionBoxes() {
            console.log("Test JS loaded - initializeQuestionBoxes");
            questionBoxesContainer.innerHTML = '';
            for (let i = 1; i <= totalQuestions; i++) {
                const box = document.createElement('div');
                box.className = 'box';
                box.id = `box-${i}`;
                box.textContent = i;
                box.addEventListener('click', () => showQuestion(i));
                questionBoxesContainer.appendChild(box);
            }
            console.log("Question boxes initialized");
        }

        // Show a specific question
        function showQuestion(questionNumber) {
            if (questionNumber < 1 || questionNumber > totalQuestions) return;

            questionCards.forEach(card => card.classList.remove('active'));
            document.getElementById(`question-card-${questionNumber}`).classList.add('active');

            currentQuestion = questionNumber;
            updatePaginationButtons();
            highlightQuestionBox(questionNumber);
        }

        // Update pagination buttons state
        function updatePaginationButtons() {
            prevBtn.disabled = currentQuestion === 1;
            nextBtn.disabled = currentQuestion === totalQuestions;
        }

        // Highlight the current question box
        function highlightQuestionBox(questionNumber) {
            document.querySelectorAll('.question-boxes .box').forEach(box => {
                box.classList.remove('active');
            });
            document.getElementById(`box-${questionNumber}`).classList.add('active');
        }

        // Show next question
        function showNextQuestion() {
            showQuestion(currentQuestion + 1);
        }

        // Show previous question
        function showPreviousQuestion() {
            showQuestion(currentQuestion - 1);
        }

        // Mark question as answered
        function markAnswered(questionId) {
            answeredQuestions.add(questionId);
            updateBoxStatus(questionId);
            checkAllAnswered();
        }

        // Toggle doubt status
        function toggleDoubt(questionId) {
            const doubtBtn = document.getElementById(`doubt-btn-${questionId}`);
            
            if (doubtQuestions.has(questionId)) {
                doubtQuestions.delete(questionId);
                doubtBtn.textContent = '❓ Mark as Doubt';
                doubtBtn.classList.remove('doubt');
            } else {
                doubtQuestions.add(questionId);
                doubtBtn.textContent = '✅ Remove Doubt';
                doubtBtn.classList.add('doubt');
            }
            updateBoxStatus(questionId);
        }

        // Update question box status (answered/doubt)
        function updateBoxStatus(questionId) {
            const box = document.getElementById(`box-${questionId}`);
            
            box.classList.remove('answered', 'doubt');
            if (doubtQuestions.has(questionId)) {
                box.classList.add('doubt');
            } else if (answeredQuestions.has(questionId)) {
                box.classList.add('answered');
            }
        }

        // Check if all questions are answered
        function checkAllAnswered() {
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn && answeredQuestions.size === totalQuestions) {
                submitBtn.disabled = false;
                submitBtn.classList.add('enabled');
            }
        }

        // Start the test
        function startTest() {
            document.getElementById('instructions').style.display = 'none';
            document.getElementById('test-container').style.display = 'block';
            initializeQuestionBoxes();
            showQuestion(1);
            startTimer();
            enterFullScreen();
            setupMalpracticeCheck();
            setupVisibilityChangeHandler();
            setupKeyboardNavigation();
        }

        // Timer functionality
        let timeLimit = parseInt("{{ paper.time_limit }}", 10) * 60 || 3600;
        let timeTaken = 0;

        function startTimer() {
            updateTimerDisplay();
            timerInterval = setInterval(() => {
                if (timeLimit > 0) {
                    timeLimit--;
                    timeTaken++;
                    document.getElementById('time-taken').value = timeTaken;
                    updateTimerDisplay();
                } else {
                    endTest();
                }
            }, 1000);
        }

        function updateTimerDisplay() {
            const minutes = Math.floor(timeLimit / 60);
            const seconds = timeLimit % 60;
            document.getElementById('time').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        // Fullscreen functionality
        function enterFullScreen() {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen().catch(err => {
                    console.error('Fullscreen error:', err);
                });
            } else if (elem.mozRequestFullScreen) {
                elem.mozRequestFullScreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        }

        // Malpractice check
        function setupMalpracticeCheck() {
            malpracticeInterval = setInterval(() => {
                if (!document.fullscreenElement && 
                    !document.webkitFullscreenElement && 
                    !document.mozFullScreenElement && 
                    !document.msFullscreenElement) {
                    reportMalpractice();
                }
            }, 1000);
        }

        function reportMalpractice() {
            if (!formSubmitted) {
                document.getElementById('malpractice').value = 'true';
                document.getElementById('test-form').submit();
                formSubmitted = true;
            }
        }

        // Tab visibility change handler
        function setupVisibilityChangeHandler() {
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'hidden' && !formSubmitted) {
                    reportMalpractice();
                }
            });
        }

        // Keyboard navigation
        function setupKeyboardNavigation() {
            document.addEventListener('keydown', (event) => {
                if (event.key === 'ArrowLeft') {
                    showPreviousQuestion();
                } else if (event.key === 'ArrowRight') {
                    showNextQuestion();
                }
            });
        }

        // End test
        function endTest() {
            clearInterval(timerInterval);
            clearInterval(malpracticeInterval);
            if (!formSubmitted) {
                document.getElementById('test-form').submit();
                formSubmitted = true;
            }
        }