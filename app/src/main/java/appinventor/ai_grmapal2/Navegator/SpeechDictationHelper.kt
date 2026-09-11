package appinventor.ai_grmapal2.Navegator

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.speech.RecognizerIntent
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import java.util.Locale

class SpeechDictationHelper(
    private val activity: ComponentActivity,
    private val onTextRecognized: (String) -> Unit
) {

    private val speechLauncher: ActivityResultLauncher<Intent> =
        activity.registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK && result.data != null) {
                val matches = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                if (!matches.isNullOrEmpty()) {
                    val recognizedText = matches[0]
                    onTextRecognized(recognizedText)
                }
            }
        }

    fun startDictation() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_WEB_SEARCH
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                activity.getString(R.string.search_or_enter_url)
            )
        }

        try {
            speechLauncher.launch(intent)
        } catch (e: ActivityNotFoundException) {
            Toast.makeText(
                activity,
                activity.getString(R.string.speech_not_available),
                Toast.LENGTH_SHORT
            ).show()
        }
    }
}
