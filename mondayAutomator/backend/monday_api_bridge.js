const express = require('express');
const mondaySdk = require("monday-sdk-js");

const app = express();
app.use(express.json());

app.post('/create_board', async (req, res) => {
    console.log('Received request to create board:', JSON.stringify(req.body, null, 2));
    try {
        const { apiKey, boardData, workspaceId } = req.body;
        const monday = mondaySdk({ token: apiKey });

        const query = `mutation($name: String!, $kind: BoardKind!, $workspaceId: Int!) {
            create_board (board_name: $name, board_kind: $kind, workspace_id: $workspaceId) {
                id
            }
        }`;

        const variables = {
            name: boardData.board.name,
            kind: boardData.board.kind,
            workspaceId: parseInt(workspaceId)
        };

        console.log('Sending request to Monday.com API with variables:', JSON.stringify(variables, null, 2));

        const response = await monday.api(query, { variables });
        
        console.log('Received response from Monday.com API:', JSON.stringify(response, null, 2));

        if (response.data && response.data.create_board && response.data.create_board.id) {
            console.log('Board created successfully with ID:', response.data.create_board.id);
            res.json(response.data);
        } else {
            console.log('Board creation response does not contain expected data:', JSON.stringify(response, null, 2));
            res.status(500).json({ error: 'Unexpected response format from Monday.com API' });
        }
    } catch (error) {
        console.error('Error creating board:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Monday API bridge running on port ${PORT}`));
