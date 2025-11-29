const io = require('socket.io-client');
const server = require('../index');

describe('Socket.io Integration', () => {
    let clientSocket1, clientSocket2;

    beforeAll((done) => {
        server.listen(3001, () => {
            done();
        });
    });

    afterAll((done) => {
        server.close(done);
    });

    beforeEach((done) => {
        clientSocket1 = io('http://localhost:3001');
        clientSocket2 = io('http://localhost:3001');

        let connectedCount = 0;
        const onConnect = () => {
            connectedCount++;
            if (connectedCount === 2) done();
        };

        clientSocket1.on('connect', onConnect);
        clientSocket2.on('connect', onConnect);
    });

    afterEach(() => {
        if (clientSocket1.connected) clientSocket1.close();
        if (clientSocket2.connected) clientSocket2.close();
    });

    test('should broadcast code updates', (done) => {
        clientSocket2.on('code-update', (code) => {
            expect(code).toBe('console.log("hello")');
            done();
        });
        clientSocket1.emit('code-update', 'console.log("hello")');
    });
});
