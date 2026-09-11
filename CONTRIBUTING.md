# 🤝 Contributing to Easy Navigator

Thank you for your interest in contributing to **Easy Navigator**! We welcome bug reports, feature suggestions, documentation enhancements, and code contributions.

---

## 📋 Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for everyone. Please be respectful, inclusive, and constructive in all discussions and interactions.

---

## 🐛 Reporting Bugs
1. **Search existing issues** before submitting a new one to avoid duplicates.
2. Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).
3. Provide clear steps to reproduce the issue, your Android device model, Android OS version, and expected vs. actual behavior.

---

## 💡 Suggesting Features
1. Check existing issues or discussions to ensure the feature hasn't been proposed yet.
2. Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).
3. Clearly explain the motivation and the user benefit of the requested feature.

---

## 🛠️ Development Workflow

1. **Fork** the repository and clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/EasyNavigator.git
   cd EasyNavigator
   ```

2. **Create a branch** for your change following conventional naming:
   ```bash
   git checkout -b feat/my-awesome-feature
   # or
   git checkout -b fix/issue-description
   ```

3. **Requirements**:
   - JDK 17 or higher
   - Android SDK API 36 (Android 16 preview/target)
   - Gradle 8.11+ (provided via `./gradlew`)

4. **Verify your changes**:
   Compile and run checks before committing:
   ```bash
   ./gradlew compileDebugKotlin
   ./gradlew test
   ./gradlew assembleDebug
   ```

5. **Commit style**:
   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add new search provider`
   - `fix: prevent duplicate url encoding`
   - `docs: update screenshot guidelines`
   - `refactor: clean up webview privacy callbacks`

6. **Submit a Pull Request**:
   - Push your branch to GitHub.
   - Open a PR against the `main` branch.
   - Fill in the Pull Request template thoroughly.

---

## 📜 License
By contributing to Easy Navigator, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
