// Copyright 2000-2021 JetBrains s.r.o. and contributors. Use of this source code is governed by the Apache 2.0 license that can be found in the LICENSE file.
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import kotlinx.coroutines.launch
import java.io.*
import kotlin.io.*
import kotlin.io.path.Path
import kotlin.io.path.readLines
import kotlin.io.path.writeLines


fun readQuestion(pathToQuestions : String, switchResults: (String)->Unit) : Map<String, String>{

    try {
        var q_and_a = Path(pathToQuestions)
        var allQuestions = q_and_a.readLines()
        val formattedQuestions = mutableMapOf<String, String>()
        var cQ = ""
        for(a in 0..allQuestions.size-1){
            cQ = allQuestions.get(a).replace("(", "").replace(")","")
            formattedQuestions.put(cQ.split("|")[0], cQ.split("|")[1])
        }
        print(formattedQuestions)
        switchResults("Finished")
        return formattedQuestions
    }
    catch (e: Exception){
        switchResults("File not Found")
        return mapOf<String, String>()
    }
}


fun processAnswer(a:String):Boolean{
    if(a.contains("Yes") || a.contains("positive") || a.contains("First Char") || a.contains("Protagonist")){
        return true
    }
    return false
}


fun processQuestion(q:String):List<String>{
    if(q.contains("protagonist")){
        return listOf("Protagonist","Antagnonist")
    }
    else if(q.contains("a more frequently occurring character in the story's plot?")){
        return listOf("First Char", "Second Char")
    }
    else if(q.contains("positive relationship")){
        return listOf("Yes", "No")
    }
    else if(q.contains("positive")){
        return listOf("positive", "negative")
    }
    else{
        return listOf("Yes", "No")
    }
}


fun main() = application {
    Window(onCloseRequest = ::exitApplication) {

        Surface (color = MaterialTheme.colors.secondaryVariant) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                var PleaseEnterPathToFile by rememberSaveable() { mutableStateOf("../QG/questions_and_answers.txt") }
                TextField(
                    value = PleaseEnterPathToFile,
                    onValueChange = { PleaseEnterPathToFile = it },
                    label = { Text("Absolute File Path to a questions_and_answers.txt from the Python QG") })

                var QGButtonName by remember { mutableStateOf("Generate Questions") }
                var success by remember { mutableStateOf("") }
                val handleGenerateQuestionClick: (String) -> Unit =
                    { msg: String -> success = msg }
                //button click swap pattern from compose tutorial https://developer.android.com/codelabs/jetpack-compose-basics?continue=https%3A%2F%2Fdeveloper.android.com%2Fcourses%2Fpathways%2Fcompose%23codelab-https%3A%2F%2Fdeveloper.android.com%2Fcodelabs%2Fjetpack-compose-basics#7

                var allQuestions by remember{ mutableStateOf(mapOf<String,String>())}
                IconButton(onClick = {
                    allQuestions = readQuestion(PleaseEnterPathToFile, handleGenerateQuestionClick)
                })
                {
                    Icon(
                        Icons.Filled.Send,
                        contentDescription = "ButtonWLoadIcon",
                        tint = Color.Blue
                    )
                    Text("\n\n" + QGButtonName)
                }

                Snackbar { Text(success) }
                QGButtonName = "Read Questions"

                var isFinished by remember{ mutableStateOf(false)}
                var totalCorrect by remember { mutableStateOf(0) }
                var totalQuestions by remember { mutableStateOf(0)}
                var finalQuestions by remember{ mutableStateOf(mutableListOf<String>()) }
                if(success == "Finished" && !isFinished){
                    var question by remember { mutableStateOf("") }
                    var answer by remember { mutableStateOf("") }

                    var yes_selected by remember { mutableStateOf(false) }
                    var no_selected by remember { mutableStateOf(false) }
                    var bad_question by remember { mutableStateOf(false) }

                    var Q = mutableListOf<String>()
                    var A = mutableListOf<String>()

                    for(eachQ in allQuestions){
                        Q.add(eachQ.key)
                        A.add(eachQ.value)
                    }

                    var processedAnswer by remember { mutableStateOf(false) }
                    var processedQuestion by remember { mutableStateOf(listOf("")) }
                    var buttonLabel0 by remember { mutableStateOf("") }
                    var buttonLabel1 by remember { mutableStateOf("") }
                    var questionLabel by remember{ mutableStateOf(0)}
                    var buttonLabel by remember { mutableStateOf("Show Answer") }


                    fun changeStateOfQuiz(nextInt: Int) {
                        if(question !=""){
                            if (yes_selected == true && processedAnswer == true) {
                                totalCorrect += 1
                                totalQuestions +=1
                                finalQuestions.add(question + "|" + answer)
                            }
                            else if (no_selected == true && processedAnswer == false) {
                                totalCorrect += 1
                                totalQuestions +=1
                                finalQuestions.add(question + "|" + answer)
                            }
                            else if (bad_question) {

                            }
                            else{
                                totalQuestions +=1
                                finalQuestions.add(question + "|" + answer)
                            }
                        }

                        yes_selected = false
                        no_selected = false
                        bad_question = false
                        buttonLabel = "Show Answer"

                        if(nextInt < allQuestions.size){
                            question = Q[nextInt]
                            answer = A[nextInt]
                        }

                        else{
                            isFinished = true
                        }

                        processedAnswer = processAnswer(answer)
                        processedQuestion = processQuestion(question)
                        buttonLabel0 = processedQuestion.get(0)
                        buttonLabel1 = processedQuestion.get(1)

                    }
                    var quizStart by remember{ mutableStateOf("StartQuiz")}

                    Button(onClick = {changeStateOfQuiz(questionLabel++); quizStart = "NextQuestion";}){Text(quizStart)}
                    Column(horizontalAlignment = Alignment.Start) {
                        Text("Question: $question")
                        Row(
                            modifier = Modifier.background(Color.LightGray)
                                .size(700.dp, 100.dp)
                        ) {
                            Box(
                                modifier = Modifier.background(Color.Transparent)
                                    .size(150.dp)
                            ) {
                                Text("$buttonLabel0")
                                RadioButton(
                                    selected = yes_selected,
                                    onClick = {
                                        yes_selected = !yes_selected; no_selected =
                                        false;
                                        bad_question = false
                                    })
                            }
                            Box(
                                modifier = Modifier.background(Color.Transparent)
                                    .size(150.dp)
                            ) {
                                Text("$buttonLabel1")
                                RadioButton(
                                    selected = no_selected,
                                    onClick = {
                                        no_selected = !no_selected;yes_selected =
                                        false;bad_question = false
                                    })
                            }
                            Box(
                                modifier = Modifier.background(Color.Transparent)
                                    .size(150.dp)
                            ) {
                                Text("Remove Question")
                                RadioButton(
                                    selected = bad_question,
                                    onClick = {
                                        bad_question = !bad_question; yes_selected =
                                        false; no_selected = false
                                    })
                            }

                            Button(onClick = { buttonLabel = "$answer";}) { Text("$buttonLabel") }
                        }
                    }

                }
                else if(isFinished){
                    if(totalQuestions < 0){
                        totalQuestions = 0
                    }
                    Column{
                        Box(
                            modifier = Modifier.background(Color.Transparent)
                                .size(150.dp)
                        ) {
                            Text("Finished, Final Score is $totalCorrect / $totalQuestions")
                        }
                        var finalPath by remember { mutableStateOf("File Path where the updated questions and answers will be written (with questions removed)")}
                        TextField(
                            value = finalPath,
                            onValueChange = { finalPath = it },
                            label = { Text("Absolute File Path to a new questions and answers .txt")})

                        var sbText by remember{mutableStateOf("")}
                        Snackbar { Text(sbText)}
                        var changeSbText: (String) -> Unit =
                            { msg: String -> sbText = msg }
                        fun writeFinalQuestions(sbOutput: (String)->Unit){
                            try{
                                val toWrite = Path(finalPath)
                                toWrite.writeLines(finalQuestions)
                                sbOutput("Wrote New Question to $finalPath")
                            }
                            catch(e: Exception){
                                sbOutput("Failure")
                            }
                        }
                        Button(onClick = {writeFinalQuestions(changeSbText)}){Text("WriteQuestions")}


                    }

                }

            }
        }

    }

}


